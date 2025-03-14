# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 21:57
@Auth: shahao(Amos-Sha)
@File: base_connection.py
@IDE : PyCharm
"""

from abc import ABC, abstractmethod
from core.utils.logger import TestLogger

class BaseConnection(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.logger = TestLogger.get_logger().getChild(self.__class__.__name__)
        self._connected = False
        self._login_status = False  # 新增登录状态

    @abstractmethod
    def connect(self):
        """建立设备连接"""
        pass

    @abstractmethod
    def write(self, command: str):
        """发送命令"""
        pass
    
    @abstractmethod
    def read(self):
        """读取设备响应"""
        pass

    # @abstractmethod
    # def wait_until(self, search, timeout=60):
    #     """等待直到收到指定字符"""
    #     pass

    @abstractmethod
    def close_connection(self):
        """关闭连接"""
        pass