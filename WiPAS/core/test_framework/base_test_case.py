# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 22:03
@Auth: shahao(Amos-Sha)
@File: testcase.py
@IDE:  PyCharm
"""
from abc import ABC, abstractmethod
import logging
from typing import Any
from core.utils.logger import TestLogger

class BaseTestCase(ABC):
    def __init__(self, 
                 config: dict,
                 instrument: Any,  # 移除logger参数
                 dut_manager: Any):
        self.config = config
        self.logger = TestLogger.get_logger().getChild(self.__class__.__name__)
        self.instrument = instrument
        self.dut_manager = dut_manager

    @abstractmethod
    def setup(self):
        """测试前置操作"""
        pass
    
    @abstractmethod
    def execute(self):
        """执行测试步骤"""
        pass
    
    @abstractmethod 
    def teardown(self):
        """测试后置操作"""
        pass
    
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