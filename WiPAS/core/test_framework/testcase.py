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

class BaseTestCase(ABC):
    """测试用例基类"""
    
    def __init__(self, 
                 config: dict, 
                 logger: logging.Logger, 
                 instrument: Any):
        self.config = config
        self.logger = logger.getChild(self.__class__.__name__)  # 创建子logger
        self.instrument = instrument
        
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