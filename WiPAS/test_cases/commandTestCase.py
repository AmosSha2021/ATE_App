# -*- coding: utf-8 -*-
"""
@Time: 2025/3/13 22:03
@Auth: shahao(Amos-Sha)
@File: CommandTestCase.py
@IDE:  PyCharm
"""
from core.test_framework.base_test_case import BaseTestCase
import re

class CommandTestCase(BaseTestCase):
    def __init__(self, **kwargs):
        # 显式调用父类初始化
        super().__init__(**kwargs)  # 自动接收config['test_cases']参数

    def setup(self):
        self.logger.info("开始测试设备登录")
        if self.dut_manager:
            self.dut_manager.login()  # 第一次调用

    def _validate_Regex(self, response: str, pattern: str) -> bool:
        """新增响应验证函数"""
        try:
            # 添加空值检查
            if not pattern:
                self.logger.warning("未配置正则表达式验证模式，跳过验证")
                return True  # 或根据需求返回False
                
            compiled_pattern = re.compile(pattern)
            return bool(compiled_pattern.search(response))
        except re.error as e:
            self.logger.error(f"正则表达式错误: {pattern} | 错误: {str(e)}")
            return False

    def execute(self):
        self._execute_command_validation()
    
    def _execute_command_validation(self):
        """执行命令验证流程"""
        command_tests = self.config.get('commands_validation', [])
        self.logger.info(f"开始执行 {len(command_tests)} 条命令验证")
        
        if self.dut_manager and self.dut_manager.get_login_status():
            for test_case in command_tests:
                self._execute_single_command(test_case)

    def _execute_single_command(self, test_case: dict):
        """执行单个命令测试用例"""
        try:
            # 执行命令
            response = self._run_command(test_case)
            # 验证结果
            self._validate_command(test_case, response)
        except Exception as e:
            self.logger.error(f"命令执行异常: {test_case['command']} | 错误: {str(e)}")
            raise

    def _run_command(self, test_case: dict) -> str:
        """执行命令并返回响应"""
        # self.logger.info(f"执行命令: {test_case['command']}")
        response = self.dut_manager.send_recv_command(test_case['command'])
        self.logger.info(f"[response from DUT]: {response}")
        return response

    def _validate_command(self, test_case: dict, response: str):
        """执行命令结果验证"""
        if 'expect_regex' in test_case:
            is_valid = self._validate_Regex(response, test_case['expect_regex'])
            # status = "通过" if is_valid else "失败"
            # self.logger.info(f"验证结果: {status}")
            if is_valid:
                self.logger.info("command Regex validation pass")
            else:
                self.logger.error("command Regex validation fail")
        else:
            self.logger.warning("未配置expect_regex,跳过结果验证")

    def teardown(self):
        if self.dut_manager:
            self.dut_manager.disconnect()
            self.logger.info("测试DUT断开连接")

    def run(self):
        """执行入口"""
        self.logger.info(f"--------------------Start to run script:{self.__class__.__name__};test case: {self.config.get('test_case_id', [])}--------------------")
        try:
            self.setup()
            self.execute()
        except Exception as e:
            self.logger.error(f"执行过程中发生异常: {str(e)}")
            raise
        finally:
            self.teardown()
            self.logger.info("测试用例执行结束")