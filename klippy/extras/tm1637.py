# Support for TM1637 7-segment display
#
# Copyright (C) 2023  Jookia <contact@jookia.org>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging

# Segments

seg_a = 1 << 0
seg_b = 1 << 1
seg_c = 1 << 2
seg_d = 1 << 3
seg_e = 1 << 4
seg_f = 1 << 5
seg_g = 1 << 6
seg_dp = 1 << 7

dig_0 = seg_a | seg_b | seg_c | seg_d | seg_e | seg_f
dig_1 = seg_b | seg_c
dig_2 = seg_a | seg_b | seg_d | seg_e | seg_g
dig_3 = seg_a | seg_b | seg_c | seg_d | seg_g
dig_4 = seg_b | seg_c | seg_f | seg_g
dig_5 = seg_a | seg_c | seg_d | seg_f | seg_g
dig_6 = seg_a | seg_c | seg_d | seg_e | seg_f | seg_g
dig_7 = seg_a | seg_b | seg_c
dig_8 = seg_a | seg_b | seg_c | seg_d | seg_e | seg_f | seg_g
dig_9 = seg_a | seg_b | seg_c | seg_d | seg_f | seg_g

digits = [dig_0, dig_1, dig_2, dig_3, dig_4, dig_5, dig_6, dig_7, dig_8, dig_9]

# Printer class that controls TM1637 chip
class TM1637:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = ' '.join(config.get_name().split()[1:])
        self.mcu = mcu = self.printer.lookup_object('mcu')
        self.oid = oid = mcu.create_oid()
        pins = self.printer.lookup_object('pins')
        clk_pin = pins.lookup_pin(config.get("clk_pin"))['pin']
        dio_pin = pins.lookup_pin(config.get("dio_pin"), share_type="tm1637_dio")['pin']
        mcu.add_config_cmd("config_tm1637 oid=%d clk_pin=%s dio_pin=%s"
            % (oid, clk_pin, dio_pin))
        mcu.register_config_callback(self._build_config)
        self.printer.register_event_handler("klippy:connect", self._handle_connect)
    def _build_config(self):
        self.send_cmd = self.mcu.lookup_command("tm1637_send oid=%c data=%*s")
    def _handle_connect(self):
        grid = [digits[1], digits[2] | seg_dp, digits[3], digits[4], 0x00, 0x00]
        cmd1 = [0b01000000] # normal mode, automatic address, write data to display register
        cmd2 = [0b11000000] + grid # C0H, write grid
        cmd3 = [0b10001000] # display on, 1/16 pulse width
        bytes = cmd1 + cmd2 + cmd3
        self.send_cmd.send([self.oid, bytes])

def load_config(config):
    return TM1637(config)

def load_config_prefix(config):
    return TM1637(config)
