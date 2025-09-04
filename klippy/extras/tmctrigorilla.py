# TMC driver for the Anycubic Trigorilla v1.0.4 board
#
# Copyright (C) 2019  Stephan Oelze <stephan.oelze@gmail.com>
# Copyright (C) 2023  Jookia <contact@jookia.org>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
from . import tmc2208, tmc2209, tmc2130, tmc, tmc_uart

# The Anycubic Trigorilla v1.0.4 board has a hardware bug: It assigns both
# the TMC2208 extruder controller and TMC2209 X stepper controller to the
# same UART address, leaving a bus conflict. This means we can't read from
# the two chips, but we can still write to both at the same time.
#
# This module is identical to the TMC2209 module but disables register writing
# functionality. only supports write registers and write functionality. One
# instance of this module is intended to control both the X stepper and
# extruder. This ensures coherency between registers. The TMC2209 features are
# supported as the TMC2208 ignores them.
#
# Things this driver won't support:
# - Dumping registers
# - Phase tracking
# - Different registers on the extruder or X stepper
# - Reading diagnostics if the controller stops
# - Checking for UART transmission failures

TMC_FREQUENCY = 12000000.0

Registers = tmc2209.Registers
ReadRegisters = tmc2209.ReadRegisters
Fields = tmc2209.Fields
FieldFormatters = tmc2209.FieldFormatters

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
        # Setup printer callbacks
        self.printer = config.get_printer()
        self.printer.register_event_handler(
            "klippy:mcu_identify", self._handle_mcu_identify
        )
        # Setup mcu communication
        self.fields = tmc.FieldHelper(
            Fields, tmc2208.SignedFields, FieldFormatters
        )
        self.mcu_tmc = tmc_uart.MCU_TMC_uart(
            config, Registers, self.fields, 3, TMC_FREQUENCY, False
        )
        # Setup fields for UART
        self.fields.set_field("pdn_disable", True)
        self.fields.set_field("senddelay", 2)  # Avoid tx errors on shared uart
        # Allow virtual pins to be created
        tmc.TMCVirtualPinHelper(config, self.mcu_tmc)
        # Register commands
        current_helper = tmc2130.TMC2130CurrentHelper(config, self.mcu_tmc)
        cmdhelper = tmc.TMCCommandHelper(
            config, self.mcu_tmc, current_helper, False
        )
        cmdhelper.setup_register_dump(ReadRegisters)
        self.get_phase_offset = cmdhelper.get_phase_offset
        self.get_status = cmdhelper.get_status
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

    def _handle_mcu_identify(self):
        # This is a little nasty but we need to inform the extruder's stepper
        # to use double steps like the tmc driver does otherwise we get
        # significant over-extrusion
        extruder = self.printer.lookup_object("extruder")
        stepper = extruder.extruder_stepper.stepper
        stepper.setup_default_pulse_duration(0.000000100, True)


def load_config_prefix(config):
    return TMCTRIGORILLA(config)
