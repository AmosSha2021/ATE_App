# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 22:03
@Auth: shahao(Amos-Sha)
@File: dut_telnet.py
@IDE:  PyCharm
"""

import telnetlib
from typing import Optional
from .dut_connection_base import DUT_Connection_Base
from core.utils.logger import TestLogger
import re
import yaml
import logging
import time

class DUTTelnet(DUT_Connection_Base):
    def __init__(self,  config, encoding='utf-8'):  # 修改初始化参数为config字典
        super().__init__(config)
        # 从配置中获取参数（带默认值）
        self.logger = TestLogger.get_logger().getChild(self.__class__.__name__)
        self.host = config['host']
        self.port = config['port']
        self.username = config['username']
        self.password = config['password']
        self.timeout = config['timeout']
        self.max_retries = 3
        self.encoding = encoding
        self.tn: Optional[telnetlib.Telnet] = None


    def _expect(self, patterns: list[re.Pattern]) -> tuple[int, re.Match, bytes]:
        """
        内部方法：使用正则表达式匹配多个可能的提示符
        :param patterns: 正则表达式列表
        :return: 匹配到的内容 (index, match, output)
        """
        if not self.tn:
            raise Exception("Telnet connection not setup")

        for _ in range(self.max_retries):
            try:
                # 读取 Telnet 输出
                index, match, output = self.tn.expect(patterns, timeout=self.timeout)
                #print(output)
                self.logger.info(f"匹配到的内容: {output}")
                if index == -1:  # 未匹配到任何模式
                    raise Exception(f"expected string value fail: {patterns}")
                return index, match, output
            except Exception as e:
                self.logger.warning(f"matching fail,try again... errors: {e}")
                time.sleep(1)  # 等待 1 秒后重试
        raise Exception(f"can not matching the expected value: {patterns}")
    
    def login(self) -> None:

        try:
            # 创建 Telnet 连接
            self.tn = telnetlib.Telnet(self.host, self.port, self.timeout)
            if not self.tn:
                raise Exception("Telnet connection failed")
            self.logger.info(f"connected to {self.host}:{self.port} done!")

            # 匹配登录提示符（忽略大小写）
            login_patterns = [
                re.compile(p.encode(self.encoding), re.IGNORECASE)
                for p in self.config.get('login_prompts', [r'.*login:.*'])
            ]
            index, match, output = self._expect(login_patterns)
            self.tn.write(self.username.encode(self.encoding) + b"\n")

            # 匹配密码提示符（忽略大小写）
            password_patterns = [
                re.compile(p.encode(self.encoding), re.IGNORECASE)
                for p in self.config.get('password_prompts', [r'.*password:.*'])
            ]
            index, match, output = self._expect(password_patterns)
            self.tn.write(self.password.encode(self.encoding) + b"\n")

            # 检查是否登录成功
            prompt_patterns = [re.compile(b"<H3C>", re.IGNORECASE),
                              re.compile(b"#", re.IGNORECASE)]
            index, match, output = self._expect(prompt_patterns)
            if b"Login incorrect" in output:
                self._login_status = False  # 更新登录状态
                raise Exception("login fail：the wrong username or password")
            self._login_status = True  # 更新登录状态
            self.logger.info("login success and into normal account!")

        except Exception as e:
            self._login_status = False  # 更新登录状态
            self.logger.error(f"login or switch into root fail: {e}")
            self.close()
            raise

    def send_recv_command(self, command: str) -> str:
        """发送命令并返回响应"""
        if not self.tn:
            raise Exception("Telnet connection failed")

        try:
            self.logger.info(f"[command to DUT]: {command}")
            self.tn.write(command.encode(self.encoding) + b"\n")
            
            # 使用字节字符串模式代替正则表达式对象
            prompt_patterns = [
                p.encode(self.encoding)
                for p in self.config.get('success_prompts', [r'#', r'<\w+>'])
            ]
            
            output = b''
            while True:
                # 使用 telnetlib 原生匹配模式
                index, match, data = self.tn.expect(prompt_patterns, timeout=self.timeout)
                output += data
                if index != -1:  # 匹配成功
                    break

            # 解码前移除命令回显
            response = output.decode(self.encoding).replace(command, '').strip()
            self.logger.debug(f"原始响应数据:\n{response}")
            return response

        except Exception as e:
            self.logger.error(f"命令执行失败: {e}")
            raise
    def disconnect(self):  # 实现抽象方法
        """断开设备连接"""
        self.close()

    # 保持原有的 close 方法不变
    def close(self) -> None:
        """关闭 Telnet 连接"""
        if self.tn:
            self.tn.close()
            self.tn = None


