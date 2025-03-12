# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 22:03
@Auth: shahao(Amos-Sha)
@File: dut_manager.py
@IDE:  PyCharm
"""
from core.dut.dut_connection_base import DUT_Connection_Base
from importlib import import_module
from core.utils.logger import TestLogger

class DUTManager:
    def __init__(self):
        
        # 使用统一日志器创建子logger
        self.logger = TestLogger.get_logger().getChild("DUTManager")
        self._dut_connection_registry = {
            'telnet': ('core.dut.dut_telnet', 'DUTTelnet')
        }
        

    # 改为实例方法
    def create_dut(self, dut_config: dict) -> DUT_Connection_Base:
        """根据配置创建DUT实例"""
        dut_type = dut_config['type']
        module_path, class_name = self._dut_connection_registry[dut_type]
        
        self.logger.info(f"Creating {dut_type} connection...")
        module = import_module(module_path)
        dut_class = getattr(module, class_name)
        return dut_class(dut_config)