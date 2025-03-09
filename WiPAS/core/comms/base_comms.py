# -*- coding: utf-8 -*-
"""
@Time ： 2025/3/7 21:57
@Auth ： shahao(Amos-Sha)
@File ：base_comms.py
@IDE ：PyCharm
"""

from abc import ABC, abstractmethod


class BaseCommunication(ABC):
    @abstractmethod
    def connect(self):
        """建立设备连接"""
        pass

    @abstractmethod
    def send_command(self, command: str, timeout: float = 5.0):
        """发送命令并返回响应"""
        pass

    @abstractmethod
    def disconnect(self):
        """关闭连接"""
        pass