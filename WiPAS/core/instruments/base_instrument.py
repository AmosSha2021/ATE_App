# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 22:03
@Auth: shahao(Amos-Sha)
@File: base_instrument.py
@IDE:  PyCharm
"""
from abc import ABC, abstractmethod
import logging

class BaseInstrument(ABC):
    """仪器驱动基类"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger.getChild(self.__class__.__name__)
        self._connected = False
        
    @abstractmethod
    def connect(self, **kwargs):
        """连接仪器"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """断开连接"""
        pass
    
    @abstractmethod
    def measure_tx_power(self) -> float:
        """测量发射功率"""
        pass
    
    @abstractmethod
    def measure_rx_sensitivity(self) -> float:
        """测量接收灵敏度"""
        pass
    
    @property
    def connected(self) -> bool:
        """连接状态"""
        return self._connected
    
    def _validate_connection(self):
        if not self.connected:
            raise ConnectionError("仪器未连接")