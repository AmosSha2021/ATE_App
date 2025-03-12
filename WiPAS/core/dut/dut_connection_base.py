# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 22:03
@Auth: shahao(Amos-Sha)
@File: dut_base.py
@IDE:  PyCharm
"""

from abc import ABC, abstractmethod
from core.utils.logger import TestLogger

class DUT_Connection_Base(ABC):
    """DUT连接基类"""
    def __init__(self, config: dict):
        self.config = config
        self.logger = TestLogger.get_logger().getChild(self.__class__.__name__)
        self._connected = False
        self._login_status = False  # 新增登录状态

    def get_login_status(self) -> bool:
        """获取登录状态"""
        return self._login_status

    @abstractmethod
    def login(self):
        """建立设备连接"""
        pass

    @abstractmethod
    def send_recv_command(self, command: str) -> str:
        """发送命令并返回响应"""
        pass

    @abstractmethod
    def disconnect(self):
        """断开设备连接"""
        pass

    @property
    def is_connected(self) -> bool:
        return self._connected