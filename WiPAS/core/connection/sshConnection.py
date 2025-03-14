# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 21:57
@Auth: shahao(Amos-Sha)
@File: sshConnection.py
@IDE : PyCharm
"""
from .base_connection import BaseConnection
from core.utils.logger import TestLogger
import paramiko
import re
import time

class SSHConnection(BaseConnection):
    def __init__(self, config: dict):
        self.logger = TestLogger.get_logger().getChild(self.__class__.__name__)
        self.ssh_config = config
        self.ssh_handle = paramiko.SSHClient()
        self.ssh_handle.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.input, self.output, self.error = (None, None, None)
        self.connected = False
        self.channel = None  # 新增通道对象

    def connect(self):
        if not self.connected:
            self.ssh_handle.connect(self.comport_config_dict["ip"],
                                    port=int(self.comport_config_dict.get("port", 22)),
                                    username=self.comport_config_dict["username"],
                                    password=self.comport_config_dict["password"],
                                    timeout=15)
            self.connected = True
            self.channel = self.ssh_handle.invoke_shell()  # 创建持久通道
            self._login()  # 新增登录验证

    def _login(self):
        """处理登录验证提示"""
        login_prompt = re.compile(r"(login:|username|password)", re.IGNORECASE)
        response = self._read_channel(timeout=5)
        if login_prompt.search(response):
            self.channel.send(self.ssh_config["username"] + "\n")
        if "password" in response.lower():
            self.channel.send(self.ssh_config["password"] + "\n")

    def write(self, command):
        """优化命令发送"""
        if not self.connected:
            self.connect()
            
        self.channel.send(command + "\n")  # 统一添加换行符
        time.sleep(0.1)  # 等待命令执行

    def read(self, timeout=1.0):
        """增强版读取"""
        end_time = time.time() + timeout
        output = []
        
        while time.time() < end_time:
            if self.channel.recv_ready():
                data = self.channel.recv(1024).decode('utf-8', errors='ignore')
                output.append(data)
            else:
                time.sleep(0.1)
                
        return ''.join(output)

    def _read_channel(self, timeout):
        # 与 read() 方法类似的读取逻辑
        return self.output.read().decode()
    
    