# Support for micro-controller chip based temperature sensors
#
# Copyright (C) 2020  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging

from .danger_options import get_danger_options

SAMPLE_TIME = 0.001
SAMPLE_COUNT = 8
REPORT_TIME = 0.300
RANGE_CHECK_COUNT = 4


class PrinterTemperatureMCU:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.base_temperature = self.slope = None
        self.temp1 = self.adc1 = self.temp2 = self.adc2 = None
        self.min_temp = self.max_temp = 0.0
        self.debug_read_cmd = None
        # Read config
        mcu_name = config.get("sensor_mcu", "mcu")
        self.reference_voltage = config.getfloat(
            "reference_voltage", default=3.3
        )
        self.temp1 = config.getfloat("sensor_temperature1", None)
        if self.temp1 is not None:
            self.adc1 = config.getfloat("sensor_adc1", minval=0.0, maxval=1.0)
            self.temp2 = config.getfloat("sensor_temperature2", None)
            if self.temp2 is not None:
                self.adc2 = config.getfloat(
                    "sensor_adc2", minval=0.0, maxval=1.0
                )
        # Setup ADC port
        ppins = config.get_printer().lookup_object("pins")
        self.mcu_adc = ppins.setup_pin(
            "adc", "%s:ADC_TEMPERATURE" % (mcu_name,)
        )
        self.mcu_adc.setup_adc_callback(REPORT_TIME, self.adc_callback)
        query_adc = config.get_printer().load_object(config, "query_adc")
        query_adc.register_adc(config.get_name(), self.mcu_adc)

        if get_danger_options().temp_ignore_limits:
            self._danger_check_count = 0
        else:
            self._danger_check_count = RANGE_CHECK_COUNT

        # Register callbacks
        if self.printer.get_start_args().get("debugoutput") is not None:
            self.mcu_adc.setup_minmax(
                SAMPLE_TIME,
                SAMPLE_COUNT,
                range_check_count=self._danger_check_count,
            )
            return
        self.mcu_adc.get_mcu().register_config_callback(self._build_config)

    def setup_callback(self, temperature_callback):
        self.temperature_callback = temperature_callback

    def get_report_time_delta(self):
        return REPORT_TIME

    def adc_callback(self, read_time, read_value):
        temp = self.base_temperature + read_value * self.slope
        self.temperature_callback(read_time + SAMPLE_COUNT * SAMPLE_TIME, temp)

    def setup_minmax(self, min_temp, max_temp):
        self.min_temp = min_temp
        self.max_temp = max_temp

    def calc_adc(self, temp):
        return (temp - self.base_temperature) / self.slope

    def calc_base(self, temp, adc):
        return temp - adc * self.slope

    def _build_config(self):
        # Obtain mcu information
        _mcu = self.mcu_adc.get_mcu()
        self.debug_read_cmd = _mcu.lookup_query_command(
            "debug_read order=%c addr=%u", "debug_result val=%u"
        )
        self.mcu_type = _mcu.get_constants().get("MCU", "")
        # Run MCU specific configuration
        cfg_funcs = [
            ("rp2", self.config_rp2040),
            ("sam3", self.config_sam3),
            ("sam4", self.config_sam4),
            ("same70", self.config_same70),
            ("samd21", self.config_samd21),
            ("samd51", self.config_samd51),
            ("same5", self.config_samd51),
            ("stm32f1", self.config_stm32f1),
            ("stm32f2", self.config_stm32f2),
            ("stm32f4", self.config_stm32f4),
            ("stm32f042", self.config_stm32f0x2),
            ("stm32f070", self.config_stm32f070),
            ("stm32f072", self.config_stm32f0x2),
            ("stm32g0", self.config_stm32g0),
            ("stm32g4", self.config_stm32g0),
            ("stm32l4", self.config_stm32g0),
            ("stm32h723", self.config_stm32h723),
            ("stm32h7", self.config_stm32h7),
            ("gd32e230x8", self.config_gd32e230x8),
            ("gd32f303xe", self.config_gd32f303xe),
            ("gd32f303xb", self.config_gd32f303xb),
            ("", self.config_unknown),
        ]
        for name, func in cfg_funcs:
            if self.mcu_type.startswith(name):
                func()
                break
        logging.info(
            "mcu_temperature '%s' nominal base=%.6f slope=%.6f",
            _mcu.get_name(),
            self.base_temperature,
            self.slope,
        )
        # Setup manual base/slope override
        if self.temp1 is not None:
            if self.temp2 is not None:
                self.slope = (self.temp2 - self.temp1) / (self.adc2 - self.adc1)
            self.base_temperature = self.calc_base(self.temp1, self.adc1)
        # Setup min/max checks
        adc_range = [self.calc_adc(t) for t in [self.min_temp, self.max_temp]]
        self.mcu_adc.setup_minmax(
            SAMPLE_TIME,
            SAMPLE_COUNT,
            minval=min(adc_range),
            maxval=max(adc_range),
            range_check_count=self._danger_check_count,
        )
        self.mcu_adc._build_config()

    def config_unknown(self):
        raise self.printer.config_error(
            "MCU temperature not supported on %s" % (self.mcu_type,)
        )

    def config_gd32e230x8(self):
        self.slope = 3.3 / -0.004300
        self.base_temperature = self.calc_base(25.0, 1.45 / 3.3)

    def config_gd32f303xe(self):
        self.slope = 3.3 / -0.004100
        self.base_temperature = self.calc_base(25.0, 1.45 / 3.3)

    def config_gd32f303xb(self):
        self.slope = 3.3 / -0.004100
        self.base_temperature = self.calc_base(25.0, 1.45 / 3.3)

    def config_rp2040(self):
        self.slope = self.reference_voltage / -0.001721
        self.base_temperature = self.calc_base(
            27.0, 0.706 / self.reference_voltage
        )

    def config_sam3(self):
        self.slope = self.reference_voltage / 0.002650
        self.base_temperature = self.calc_base(
            27.0, 0.8 / self.reference_voltage
        )

    def config_sam4(self):
        self.slope = self.reference_voltage / 0.004700
        self.base_temperature = self.calc_base(
            27.0, 1.44 / self.reference_voltage
        )

    def config_same70(self):
        self.slope = self.reference_voltage / 0.002330
        self.base_temperature = self.calc_base(
            25.0, 0.72 / self.reference_voltage
        )

    def config_samd21(self, addr=0x00806030):
        def get1v(val):
            if val & 0x80:
                val = 0x100 - val
            return 1.0 - val / 1000.0

        cal1 = self.read32(addr)
        cal2 = self.read32(addr + 4)
        room_temp = ((cal1 >> 0) & 0xFF) + ((cal1 >> 8) & 0xF) / 10.0
        hot_temp = ((cal1 >> 12) & 0xFF) + ((cal1 >> 20) & 0xF) / 10.0
        room_1v = get1v((cal1 >> 24) & 0xFF)
        hot_1v = get1v((cal2 >> 0) & 0xFF)
        room_adc = (
            ((cal2 >> 8) & 0xFFF) * room_1v / (self.reference_voltage * 4095.0)
        )
        hot_adc = (
            ((cal2 >> 20) & 0xFFF) * hot_1v / (self.reference_voltage * 4095.0)
        )
        self.slope = (hot_temp - room_temp) / (hot_adc - room_adc)
        self.base_temperature = self.calc_base(room_temp, room_adc)

    def config_samd51(self):
        self.config_samd21(addr=0x00800100)

    def config_stm32f1(self):
        self.slope = self.reference_voltage / -0.004300
        self.base_temperature = self.calc_base(
            25.0, 1.43 / self.reference_voltage
        )

    def config_stm32f2(self):
        self.slope = self.reference_voltage / 0.002500
        self.base_temperature = self.calc_base(
            25.0, 0.76 / self.reference_voltage
        )

    def config_stm32f4(self, addr1=0x1FFF7A2C, addr2=0x1FFF7A2E):
        cal_adc_30 = (
            self.read16(addr1) * 3.3 / (self.reference_voltage * 4095.0)
        )
        cal_adc_110 = (
            self.read16(addr2) * 3.3 / (self.reference_voltage * 4095.0)
        )
        self.slope = (110.0 - 30.0) / (cal_adc_110 - cal_adc_30)
        self.base_temperature = self.calc_base(30.0, cal_adc_30)

    def config_stm32f0x2(self):
        self.config_stm32f4(addr1=0x1FFFF7B8, addr2=0x1FFFF7C2)

    def config_stm32f070(self):
        self.slope = self.reference_voltage / -0.004300
        cal_adc_30 = self.read16(0x1FFFF7B8) / 4095.0
        self.base_temperature = self.calc_base(30.0, cal_adc_30)

    def config_stm32g0(self):
        cal_adc_30 = (
            self.read16(0x1FFF75A8) * 3.0 / (self.reference_voltage * 4095.0)
        )
        cal_adc_130 = (
            self.read16(0x1FFF75CA) * 3.0 / (self.reference_voltage * 4095.0)
        )
        self.slope = (130.0 - 30.0) / (cal_adc_130 - cal_adc_30)
        self.base_temperature = self.calc_base(30.0, cal_adc_30)

    def config_stm32h723(self):
        cal_adc_30 = (
            self.read16(0x1FF1E820) * 3.3 / (self.reference_voltage * 4095.0)
        )
        cal_adc_130 = (
            self.read16(0x1FF1E840) * 3.3 / (self.reference_voltage * 4095.0)
        )
        self.slope = (130.0 - 30.0) / (cal_adc_130 - cal_adc_30)
        self.base_temperature = self.calc_base(30.0, cal_adc_30)

    def config_stm32h7(self):
        cal_adc_30 = (
            self.read16(0x1FF1E820) * 3.3 / (self.reference_voltage * 65535.0)
        )
        cal_adc_110 = (
            self.read16(0x1FF1E840) * 3.3 / (self.reference_voltage * 65535.0)
        )
        self.slope = (110.0 - 30.0) / (cal_adc_110 - cal_adc_30)
        self.base_temperature = self.calc_base(30.0, cal_adc_30)

    def read16(self, addr):
        params = self.debug_read_cmd.send([1, addr])
        return params["val"]

    def read32(self, addr):
        params = self.debug_read_cmd.send([2, addr])
        return params["val"]


def load_config(config):
    pheaters = config.get_printer().load_object(config, "heaters")
    pheaters.add_sensor_factory("temperature_mcu", PrinterTemperatureMCU)
