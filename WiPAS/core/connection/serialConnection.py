# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 21:57
@Auth: shahao(Amos-Sha)
@File: serialConnection.py
@IDE : PyCharm
"""
from .base_connection import BaseConnection
from core.utils.logger import TestLogger
import serial

class SerialConnection(BaseConnection):
    def __init__(self, config: dict):
        self.logger = TestLogger.get_logger().getChild(self.__class__.__name__)
        self.comPort_config = config
        # self.port = config['comPort']
        # self.baudrate = config['baudrate']
        self.serial = None
        self.connected = False
        self.INPUT_BUFFER = 100

    def connect(self):
        try:
            comPort = self.comPort_config['comPort']
            baudrate = self.comPort_config['baudrate']
            time_out = self.comPort_config['time_out']
            if not self.connected:
                self.serial = serial.Serial(comPort, baudrate, timeout=time_out)
                self.connected = True
                self.logger.info(f"connected to {self.port} done!")
        except Exception as e:
            self.logger.error(f"connect fail: {e}")
            raise

    def close_connection(self):
        self.serial.close()
        self.connected = False

    def write(self, command):
        if not self.connected:
            self.connect()

        self.logger.info(f"send command: {command}")
        command += "\r"  # 保留回车符
        chunks = []
        # 分块逻辑（替代列表推导式）
        for i in range(0, len(command), self.INPUT_BUFFER): #
            end_index = i + self.INPUT_BUFFER
            chunks.append(command[i:end_index])

        # 发送所有分块
        for chunk in chunks:
            self.serial.write(chunk.encode())  # 串口通信只能发送字节数据
            # 可在此添加延迟：time.sleep(0.01)


    def read(self, timeout=1.0):
        """读取完整响应（增强版）"""
        buffer = bytearray()
        original_timeout = self.serial.timeout
        try:
            self.serial.timeout = timeout  # 临时设置读取超时
            while True:
                chunk = self.serial.read(1024)  # 分块读取
                if not chunk:
                    break
                buffer.extend(chunk)
        finally:
            self.serial.timeout = original_timeout  # 恢复原始超时
        
        try:
            return buffer.decode('utf-8')  # 统一使用UTF-8解码
        except UnicodeDecodeError as e:
            self.logger.error(f"解码失败: {e} | 原始数据: {buffer.hex()}")
            return "ERROR: DECODE FAILURE"
    
    # def wait_until(self, search, timeout=60):
    #     # Amos: no need it so far
    #     pass