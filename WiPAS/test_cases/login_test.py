# -*- coding: utf-8 -*-
"""
@Time: 2025/3/11 22:03
@Auth: shahao(Amos-Sha)
@File: login_test.py
@IDE:  PyCharm
"""
from core.test_framework.base_test_case import BaseTestCase
from core.utils.logger import TestLogger

class LoginTestCase(BaseTestCase):
    def __init__(self, **kwargs):
        # 显式调用父类初始化
        super().__init__(**kwargs)

    def setup(self):
        self.logger.info("开始测试设备登录")
        if self.dut_manager:
            self.dut_manager.login()  # 第一次调用

    def execute(self):
        if self.dut_manager:
            login_status = self.dut_manager.get_login_status()
            self.logger.info(f"当前登录状态: {login_status}")
            if login_status:
                self.dut_manager.send_recv_command("/opt/addons/am/factory_setup.sh baseAddr show")
            if not login_status:
                raise Exception("登录失败")

    def teardown(self):
        if self.dut_manager:
            self.dut_manager.disconnect()

    def run(self):
        """执行入口"""
        self.logger.info("测试用例开始执行")
        try:
            self.setup()
            self.execute()
        except Exception as e:
            self.logger.error(f"执行过程中发生异常: {str(e)}")
            raise
        finally:
            self.teardown()
            self.logger.info("测试用例执行结束")