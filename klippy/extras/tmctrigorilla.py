# TMC driver for the Anycubic Trigorilla v1.0.4 board
#
# Copyright (C) 2019  Stephan Oelze <stephan.oelze@gmail.com>
# Copyright (C) 2023  Jookia <contact@jookia.org>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
from . import tmc2208, tmc2130, tmc, tmc_uart
import logging

# The Anycubic Trigorilla v1.0.4 board has a hardware bug: It assigns both
# the TMC2208 extruder controller and TMC2209 X stepper controller to the
# same UART address, leaving a bus conflict. This means we can't read from
# the two chips, but we can still write to both at the same time.
#
# This module implements a subset of the TMC2209 and TMC2208 drivers that
# only supports write registers and write functionality. One instance of
# this module is intended to control both the X stepper and extruder. This
# ensures coherency between registers. The TMC2209 features are supported as
# the TMC2208 ignores them.
#
# A lot of this code is copied from other TMC drivers. This duplication is
# acceptable: Refactoring an entire code base to support a hardware hack
# would cause a lot of clutter and design woes.
#
# Things this driver won't support:
# - Dumping registers
# - Phase tracking
# - Different registers on the extruder or X stepper
# - Reading diagnostics if the controller stops
# - Checking for UART transmission failures

TMC_FREQUENCY = 12000000.0

Registers = {
    "GCONF": 0x00,
    "IFCNT": 0x02,
    "SLAVECONF": 0x03,
    "FACTORY_CONF": 0x07,
    "IHOLD_IRUN": 0x10,
    "TPOWERDOWN": 0x11,
    "TSTEP": 0x12,
    "TPWMTHRS": 0x13,
    "TCOOLTHRS": 0x14,
    "VACTUAL": 0x22,
    "COOLCONF": 0x42,
    "SGTHRS": 0x40,
    "CHOPCONF": 0x6C,
    "PWMCONF": 0x70,
}

Fields = {}

Fields["GCONF"] = {
    "i_scale_analog": 0x01,
    "internal_rsense": 0x01 << 1,
    "en_spreadcycle": 0x01 << 2,
    "shaft": 0x01 << 3,
    "index_otpw": 0x01 << 4,
    "index_step": 0x01 << 5,
    "pdn_disable": 0x01 << 6,
    "mstep_reg_select": 0x01 << 7,
    "multistep_filt": 0x01 << 8,
    "test_mode": 0x01 << 9,
}
Fields["IFCNT"] = {"ifcnt": 0xFF}
Fields["SLAVECONF"] = {"senddelay": 0x0F << 8}
Fields["FACTORY_CONF"] = {"fclktrim": 0x1F, "ottrim": 0x03 << 8}
Fields["IHOLD_IRUN"] = {
    "ihold": 0x1F,
    "irun": 0x1F << 8,
    "iholddelay": 0x0F << 16,
}
Fields["TPOWERDOWN"] = {"tpowerdown": 0xFF}
Fields["TSTEP"] = {"tstep": 0xFFFFF}
Fields["TPWMTHRS"] = {"tpwmthrs": 0xFFFFF}
Fields["VACTUAL"] = {"vactual": 0xFFFFFF}
Fields["CHOPCONF"] = {
    "toff": 0x0F,
    "hstrt": 0x07 << 4,
    "hend": 0x0F << 7,
    "tbl": 0x03 << 15,
    "vsense": 0x01 << 17,
    "mres": 0x0F << 24,
    "intpol": 0x01 << 28,
    "dedge": 0x01 << 29,
    "diss2g": 0x01 << 30,
    "diss2vs": 0x01 << 31,
}
Fields["PWMCONF"] = {
    "pwm_ofs": 0xFF,
    "pwm_grad": 0xFF << 8,
    "pwm_freq": 0x03 << 16,
    "pwm_autoscale": 0x01 << 18,
    "pwm_autograd": 0x01 << 19,
    "freewheel": 0x03 << 20,
    "pwm_reg": 0xF << 24,
    "pwm_lim": 0xF << 28,
}
Fields["COOLCONF"] = {
    "semin": 0x0F << 0,
    "seup": 0x03 << 5,
    "semax": 0x0F << 8,
    "sedn": 0x03 << 13,
    "seimin": 0x01 << 15,
}
Fields["SGTHRS"] = {"sgthrs": 0xFF << 0}
Fields["TCOOLTHRS"] = {"tcoolthrs": 0xFFFFF}


class TMCCommandHelperTrigorilla:
    def __init__(self, config, mcu_tmc, current_helper):
        self.printer = config.get_printer()
        self.stepper_name = " ".join(config.get_name().split()[1:])
        self.name = config.get_name().split()[-1]
        self.mcu_tmc = mcu_tmc
        self.current_helper = current_helper
        self.fields = mcu_tmc.get_fields()
        self.toff = None
        self.mcu_phase_offset = None
        self.stepper = None
        self.printer.register_event_handler(
            "klippy:mcu_identify", self._handle_mcu_identify
        )
        self.printer.register_event_handler(
            "klippy:connect", self._handle_connect
        )
        # Set microstep config options
        tmc.TMCMicrostepHelper(config, mcu_tmc)
        # Register commands
        gcode = self.printer.lookup_object("gcode")
        gcode.register_mux_command(
            "SET_TMC_FIELD",
            "STEPPER",
            self.name,
            self.cmd_SET_TMC_FIELD,
            desc=self.cmd_SET_TMC_FIELD_help,
        )
        gcode.register_mux_command(
            "INIT_TMC",
            "STEPPER",
            self.name,
            self.cmd_INIT_TMC,
            desc=self.cmd_INIT_TMC_help,
        )
        gcode.register_mux_command(
            "SET_TMC_CURRENT",
            "STEPPER",
            self.name,
            self.cmd_SET_TMC_CURRENT,
            desc=self.cmd_SET_TMC_CURRENT_help,
        )

    def _init_registers(self, print_time=None):
        # Send registers
        for reg_name in list(self.fields.registers.keys()):
            val = self.fields.registers[reg_name]  # Val may change during loop
            self.mcu_tmc.set_register(reg_name, val, print_time)

    cmd_INIT_TMC_help = "Initialize TMC stepper driver registers"

    def cmd_INIT_TMC(self, gcmd):
        logging.info("INIT_TMC %s", self.name)
        print_time = self.printer.lookup_object("toolhead").get_last_move_time()
        self._init_registers(print_time)

    cmd_SET_TMC_FIELD_help = "Set a register field of a TMC driver"

    def cmd_SET_TMC_FIELD(self, gcmd):
        field_name = gcmd.get("FIELD").lower()
        reg_name = self.fields.lookup_register(field_name, None)
        if reg_name is None:
            raise gcmd.error("Unknown field name '%s'" % (field_name,))
        value = gcmd.get_int("VALUE", None)
        velocity = gcmd.get_float("VELOCITY", None, minval=0.0)
        tmc_frequency = self.mcu_tmc.get_tmc_frequency()
        if tmc_frequency is None and velocity is not None:
            raise gcmd.error("VELOCITY parameter not supported by this driver")
        if (value is None) == (velocity is None):
            raise gcmd.error("Specify either VALUE or VELOCITY")
        if velocity is not None:
            step_dist = self.stepper.get_step_dist()
            mres = self.fields.get_field("mres")
            value = tmc.TMCtstepHelper(step_dist, mres, tmc_frequency, velocity)
        reg_val = self.fields.set_field(field_name, value)
        print_time = self.printer.lookup_object("toolhead").get_last_move_time()
        self.mcu_tmc.set_register(reg_name, reg_val, print_time)

    cmd_SET_TMC_CURRENT_help = "Set the current of a TMC driver"

    def cmd_SET_TMC_CURRENT(self, gcmd):
        ch = self.current_helper
        prev_cur, prev_hold_cur, req_hold_cur, max_cur = ch.get_current()
        run_current = gcmd.get_float(
            "CURRENT", None, minval=0.0, maxval=max_cur
        )
        hold_current = gcmd.get_float(
            "HOLDCURRENT", None, above=0.0, maxval=max_cur
        )
        if run_current is not None or hold_current is not None:
            if run_current is None:
                run_current = prev_cur
            if hold_current is None:
                hold_current = req_hold_cur
            toolhead = self.printer.lookup_object("toolhead")
            print_time = toolhead.get_last_move_time()
            ch.set_current(run_current, hold_current, print_time)
            prev_cur, prev_hold_cur, req_hold_cur, max_cur = ch.get_current()
        # Report values
        if prev_hold_cur is None:
            gcmd.respond_info("Run Current: %0.2fA" % (prev_cur,))
        else:
            gcmd.respond_info(
                "Run Current: %0.2fA Hold Current: %0.2fA"
                % (prev_cur, prev_hold_cur)
            )

    def _handle_mcu_identify(self):
        # Lookup stepper object
        force_move = self.printer.lookup_object("force_move")
        self.stepper = force_move.lookup_stepper(self.stepper_name)

    def _handle_connect(self):
        # Send init
        try:
            self._init_registers()
        except self.printer.command_error as e:
            logging.info("TMC %s failed to init: %s", self.name, str(e))


# Helper code for communicating via TMC uart
class MCU_TMC_uart_trigorilla:
    def __init__(self, config, name_to_reg, fields, max_addr, tmc_frequency):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.name_to_reg = name_to_reg
        self.fields = fields
        self.ifcnt = None
        self.instance_id, self.addr, self.mcu_uart = (
            tmc_uart.lookup_tmc_uart_bitbang(config, max_addr)
        )
        self.mutex = self.mcu_uart.mutex
        self.tmc_frequency = tmc_frequency

    def get_fields(self):
        return self.fields

    def _do_get_register(self, reg_name):
        raise self.printer.command_error(
            "Unable to read tmc uart '%s' register %s" % (self.name, reg_name)
        )

    def get_register(self, reg_name):
        with self.mutex:
            return self._do_get_register(reg_name)

    def set_register(self, reg_name, val, print_time=None):
        reg = self.name_to_reg[reg_name]
        if self.printer.get_start_args().get("debugoutput") is not None:
            return
        with self.mutex:
            # We can't check the IFCNT register so just write the value multiple
            # times in hopes this reduces errors
            for retry in range(2):
                self.mcu_uart.reg_write(
                    self.instance_id, self.addr, reg, val, print_time
                )

    def get_tmc_frequency(self):
        return self.tmc_frequency


######################################################################
# TMCTRIGORILLA printer object
######################################################################


class TMCTRIGORILLA:
    def __init__(self, config):
        # Check microstep coherency
        x_name = config.get_name().split()[-1]
        if not config.has_section(x_name):
            raise config.error(
                "Could not find config section '%s' for tmctrigorilla"
                % (x_name)
            )
        if not config.has_section("extruder"):
            raise config.error(
                "Could not find config section 'extruder' for tmctrigorilla"
            )
        x_config = config.getsection(x_name)
        extruder_config = config.getsection("extruder")
        x_microsteps = x_config.get("microsteps")
        extruder_microsteps = extruder_config.get("microsteps")
        if x_microsteps != extruder_microsteps:
            raise config.error(
                "%s and extruder microsteps must be the same for tmctrigorilla"
                % (x_name)
            )
        # Setup mcu communication
        self.fields = tmc.FieldHelper(Fields)
        self.mcu_tmc = MCU_TMC_uart_trigorilla(
            config, Registers, self.fields, 3, TMC_FREQUENCY
        )
        # Setup fields for UART
        self.fields.set_field("pdn_disable", True)
        self.fields.set_field("senddelay", 2)  # Avoid tx errors on shared uart
        # Allow virtual pins to be created
        tmc.TMCVirtualPinHelper(config, self.mcu_tmc)
        # Register commands
        current_helper = tmc2130.TMC2130CurrentHelper(config, self.mcu_tmc)
        cmdhelper = TMCCommandHelperTrigorilla(
            config, self.mcu_tmc, current_helper
        )
        # Setup basic register values
        self.fields.set_field("mstep_reg_select", True)
        tmc.TMCStealthchopHelper(config, self.mcu_tmc, TMC_FREQUENCY)
        # Allow other registers to be set from the config
        set_config_field = self.fields.set_config_field
        # GCONF
        set_config_field(config, "multistep_filt", True)
        # CHOPCONF
        set_config_field(config, "toff", 3)
        set_config_field(config, "hstrt", 5)
        set_config_field(config, "hend", 0)
        set_config_field(config, "tbl", 2)
        # IHOLDIRUN
        set_config_field(config, "iholddelay", 8)
        # PWMCONF
        set_config_field(config, "pwm_ofs", 36)
        set_config_field(config, "pwm_grad", 14)
        set_config_field(config, "pwm_freq", 1)
        set_config_field(config, "pwm_autoscale", True)
        set_config_field(config, "pwm_autograd", True)
        set_config_field(config, "freewheel", 0)
        set_config_field(config, "pwm_reg", 8)
        set_config_field(config, "pwm_lim", 12)
        # TPOWERDOWN
        set_config_field(config, "tpowerdown", 20)
        # SGTHRS
        set_config_field(config, "sgthrs", 0)


def load_config_prefix(config):
    return TMCTRIGORILLA(config)
