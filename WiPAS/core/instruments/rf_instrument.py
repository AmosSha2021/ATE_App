# -*- coding: utf-8 -*-
"""
@Time ： 2025/3/7 22:05
@Auth ： shahao(Amos-Sha)
@File ：rf_instrument.py
@IDE ：PyCharm
"""
import pyvisa


class RFInstrumentManager:
    def __init__(self, resource_name: str):
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(resource_name)

    def set_frequency(self, freq: float):
        """设置射频频率"""
        self.instrument.write(f"FREQ {freq}GHz")

    def measure_power(self) -> float:
        """测量信号功率"""
        return float(self.instrument.query("MEAS:POW?"))