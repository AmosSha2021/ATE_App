# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 22:03
@Auth: shahao(Amos-Sha)
@File: run.py
@IDE:  PyCharm
"""
import os
from core.test_management.test_manager import TestManager
from core.utils.logger import TestLogger
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

def main():
    # 初始化日志系统（替代原YAML配置）
    TestLogger.initialize(log_dir="Test_Result_logs", dut_name="ATE_Device")
    
    # 构建配置文件绝对路径
    config_path = os.path.join(os.path.dirname(__file__), "config/test_cases.yaml")
    
    # 启动测试管理
    test_manager = TestManager(config_path)  # 修改此处使用绝对路径
    test_manager.run_test_sequence()

if __name__ == "__main__":
    main()