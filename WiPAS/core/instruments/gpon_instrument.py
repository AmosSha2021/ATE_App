# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 22:03
@Auth: shahao(Amos-Sha)
@File: gpon_insrument.py
@IDE:  PyCharm
"""

import serial
from .base_instrument import BaseInstrument

# 在文件顶部添加导入
import logging

class GPonInstrument(BaseInstrument):
    def __init__(self):
        super().__init__(logging.getLogger())  # 现在可以正确获取 logger
        self._serial = None
        
    def connect(self, port='COM1', baudrate=9600):
        try:
            self._serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=1
            )
            self._connected = True
            self.logger.info(f"已连接GPON仪器 @ {port}")
        except serial.SerialException as e:
            self.logger.error(f"连接失败: {str(e)}")
            raise
            
    def disconnect(self):
        if self._serial and self._serial.is_open:
            self._serial.close()
            self._connected = False
            self.logger.info("仪器连接已断开")
            
    def measure_tx_power(self) -> float:
        self._validate_connection()
        # 实际测量逻辑示例
        self._serial.write(b'MEAS:TX_PWR?\n')
        response = self._serial.readline().decode().strip()
        return float(response)
    
    def measure_rx_sensitivity(self) -> float:
        self._validate_connection()
        # 实际测量逻辑示例
        self._serial.write(b'MEAS:RX_SENS?\n')
        response = self._serial.readline().decode().strip()
        return float(response)
    
    def get_serial_number(self) -> str:
        """获取仪器序列号"""
        self._validate_connection()
        self._serial.write(b'*IDN?\n')
        return self._serial.readline().decode().strip()