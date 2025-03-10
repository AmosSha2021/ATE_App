# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 22:03
@Auth: shahao(Amos-Sha)
@File: run.py
@IDE:  PyCharm
"""
from core.test_management.test_manager import TestManager
from core.utils.logger import TestLogger

def main():
    # 初始化日志系统（替代原YAML配置）
    TestLogger.initialize(log_dir="Test_Result_logs", dut_name="ATE_Device")
    
    # 启动测试管理
    test_manager = TestManager('config/test_cases.yaml')
    test_manager.run_test_sequence()

if __name__ == "__main__":
    main()