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
import argparse  # 新增导入

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

def main():
    # 新增参数解析
    parser = argparse.ArgumentParser(description='执行自动化测试套件')
    parser.add_argument('--cases', nargs='*', 
                       help='指定要执行的测试用例ID(空格分隔多个ID)')
    args = parser.parse_args()

    # 初始化日志系统
    TestLogger.initialize(log_dir="Test_Result_logs", dut_name="ATE_Device")
    
    # 构建配置文件绝对路径
    config_path = os.path.join(os.path.dirname(__file__), "config/test_cases.yaml")
    
    # 启动测试管理（新增selected_cases参数）
    test_manager = TestManager(config_path, selected_cases=args.cases)
    test_manager.run_test_sequence()

if __name__ == "__main__":
    '''
    # 执行单个用例
    python run.py --cases TC001

    # 执行多个用例
    python run.py --cases TC001 TC003

    # 不指定参数则执行全部用例
    python run.py
    '''
    main()