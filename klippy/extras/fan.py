# Printer cooling fan
#
# Copyright (C) 2016-2020  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
from . import pulse_counter

FAN_MIN_TIME = 0.100


class Fan:
    def __init__(self, config, default_shutdown_speed=0.0):
        self.printer = config.get_printer()
        self.last_fan_value = 0.0
        self.last_fan_time = 0.0
        self.last_pwm_value = 0.0
        # Read config
        self.kick_start_time = config.getfloat(
            "kick_start_time", 0.1, minval=0.0
        )
        self.min_power = config.getfloat(
            "min_power", default=None, minval=0.0, maxval=1.0
        )
        self.off_below = config.getfloat(
            "off_below", default=None, minval=0.0, maxval=1.0
        )
        if self.off_below is not None:
            config.deprecate("off_below")
        self.initial_speed = config.getfloat(
            "initial_speed", default=None, minval=0.0, maxval=1.0
        )

        # handles switchover of variable
        # if new var is not set, and old var is, set new var to old var
        # if new var is not set and neither is old var, set new var to default of 0.0
        # if new var is set, use new var
        if self.min_power is not None and self.off_below is not None:
            raise config.error(
                "min_power and off_below are both set. Remove one!"
            )
        if self.min_power is None:
            if self.off_below is None:
                # both unset, set to 0.0
                self.min_power = 0.0
            else:
                self.min_power = self.off_below

        self.max_power = config.getfloat(
            "max_power", 1.0, above=0.0, maxval=1.0
        )
        if self.min_power > self.max_power:
            raise config.error(
                "min_power=%f can't be larger than max_power=%f"
                % (self.min_power, self.max_power)
            )

        cycle_time = config.getfloat("cycle_time", 0.010, above=0.0)
        hardware_pwm = config.getboolean("hardware_pwm", False)
        shutdown_speed = config.getfloat(
            "shutdown_speed", default_shutdown_speed, minval=0.0, maxval=1.0
        )
        # Setup pwm object
        ppins = self.printer.lookup_object("pins")
        self.mcu_fan = ppins.setup_pin("pwm", config.get("pin"))
        self.mcu_fan.setup_max_duration(0.0)
        self.mcu_fan.setup_cycle_time(cycle_time, hardware_pwm)

        if hardware_pwm:
            shutdown_power = max(0.0, min(self.max_power, shutdown_speed))
        else:
            # the config allows shutdown_power to be > 0 and < 1, but it is validated
            # in MCU_pwm._build_config().
            shutdown_power = max(0.0, shutdown_speed)

        self.mcu_fan.setup_start_value(0.0, shutdown_power)
        self.enable_pin = None
        enable_pin = config.get("enable_pin", None)
        if enable_pin is not None:
            self.enable_pin = ppins.setup_pin("digital_out", enable_pin)
            self.enable_pin.setup_max_duration(0.0)

        # Setup tachometer
        self.tachometer = FanTachometer(config)

        # Register callbacks
        self.printer.register_event_handler(
            "gcode:request_restart", self._handle_request_restart
        )
        self.printer.register_event_handler("klippy:ready", self._handle_ready)

    def get_mcu(self):
        return self.mcu_fan.get_mcu()

    def set_speed(self, print_time, value):
        if value == self.last_fan_value:
            return
        if value > 0:
            # Scale value between min_power and max_power
            value = min(value, 1.0)
            pwm_value = (
                value * (self.max_power - self.min_power) + self.min_power
            )
        else:
            pwm_value = 0
        print_time = max(self.last_fan_time + FAN_MIN_TIME, print_time)
        if self.enable_pin:
            if value > 0 and self.last_fan_value == 0:
                self.enable_pin.set_digital(print_time, 1)
            elif value == 0 and self.last_fan_value > 0:
                self.enable_pin.set_digital(print_time, 0)
        if (
            value
            and value < self.max_power
            and self.kick_start_time
            and (not self.last_fan_value or value - self.last_fan_value > 0.5)
        ):
            # Run fan at full speed for specified kick_start_time
            self.mcu_fan.set_pwm(print_time, self.max_power)
            print_time += self.kick_start_time
        self.mcu_fan.set_pwm(print_time, pwm_value)
        self.last_pwm_value = pwm_value
        self.last_fan_time = print_time
        self.last_fan_value = value

    def set_speed_from_command(self, value):
        toolhead = self.printer.lookup_object("toolhead")
        toolhead.register_lookahead_callback(
            (lambda pt: self.set_speed(pt, value))
        )

    def _handle_request_restart(self, print_time):
        self.set_speed(print_time, 0.0)

    def _handle_ready(self):
        if self.initial_speed:
            self.set_speed_from_command(self.initial_speed)

    def get_status(self, eventtime):
        tachometer_status = self.tachometer.get_status(eventtime)
        return {
            "power": self.last_pwm_value,
            "value": self.last_fan_value,
            "speed": self.last_fan_value * self.max_power,
            "rpm": tachometer_status["rpm"],
        }


class FanTachometer:
    def __init__(self, config):
        printer = config.get_printer()
        self._freq_counter = None

        pin = config.get("tachometer_pin", None)
        if pin is not None:
            self.ppr = config.getint("tachometer_ppr", 2, minval=1)
            poll_time = config.getfloat(
                "tachometer_poll_interval", 0.0015, above=0.0
            )
            sample_time = 1.0
            self._freq_counter = pulse_counter.FrequencyCounter(
                printer, pin, sample_time, poll_time
            )

    def get_status(self, eventtime):
        if self._freq_counter is not None:
            rpm = self._freq_counter.get_frequency() * 30.0 / self.ppr
        else:
            rpm = None
        return {"rpm": rpm}


class PrinterFan:
    def __init__(self, config):
        self.fan = Fan(config)
        # Register commands
        gcode = config.get_printer().lookup_object("gcode")
        gcode.register_command("M106", self.cmd_M106)
        gcode.register_command("M107", self.cmd_M107)

    def get_status(self, eventtime):
        return self.fan.get_status(eventtime)

    def cmd_M106(self, gcmd):
        # Set fan speed
        value = gcmd.get_float("S", 255.0, minval=0.0) / 255.0
        self.fan.set_speed_from_command(value)

    def cmd_M107(self, gcmd):
        # Turn fan off
        self.fan.set_speed_from_command(0.0)


def load_config(config):
    return PrinterFan(config)
