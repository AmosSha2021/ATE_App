# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 22:03
@Auth: shahao(Amos-Sha)
@File: test_manager.py
@IDE:  PyCharm
"""

from typing import List, Dict
import yaml
# 在文件顶部新增导入
from core.utils.logger import get_logger
from core.instruments.instrument_manager import InstrumentManager

class TestManager:
    def __init__(self, config_path: str):
        root_logger = get_logger()
        self.logger = root_logger.getChild("TestManager")  # 创建子 logger
        self.test_cases = self._load_test_cases(config_path)
        # 新增测试准备状态
        self._test_ready = False

    def _pre_test_setup(self):
        """测试前准备"""
        # 具体可实现的逻辑包括：
        # 1. 设备连接校验
        # 2. 测试夹具初始化
        # 3. 环境变量配置
        # 4. 测试数据加载
        self.logger.info("正在初始化测试环境...")
        # 执行实际初始化操作（示例）
        self._test_ready = True
        self.logger.info("测试环境准备就绪")

    def _post_test_cleanup(self):
        """测试后清理"""
        self.logger.info("正在清理测试资源...")
        # 执行实际清理操作（示例）
        self._test_ready = False

    def _load_test_cases(self, config_path: str) -> List[Dict]:
        """实现YAML配置加载"""
        try:
            with open(config_path, encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('test_cases', [])
        except Exception as e:
            self.logger.error(f"加载测试用例失败: {str(e)}")
            return []

    def run_test_sequence(self):
        """执行完整测试流程"""
        try:
            self._pre_test_setup()
            for case in self.test_cases:
                self._execute_test_case(case)
            self._post_test_cleanup()
        except Exception as e:
            self.logger.error(f"测试异常终止: {str(e)}")

    def _execute_test_case(self, case_config: Dict):
        """执行单个测试用例（优化版）"""
        try:
            test_class = self._load_test_class(case_config['test_class'])
            
            # 获取仪器实例
            instrument = InstrumentManager.create_instrument(
                instrument_type=case_config['instrument']['type'],
                config=case_config['instrument']['config'],
                logger=self.logger
            )
            
            test_case = test_class(
                config=case_config,
                logger=self.logger,
                instrument=instrument
            )
            test_case.run()
        finally:
            # 确保仪器断开连接
            instrument.disconnect()

    def _load_test_class(self, class_path: str):
        """动态加载测试类（新增方法）"""
        from importlib import import_module
        module_path, class_name = class_path.rsplit('.', 1)
        try:
            module = import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            self.logger.error(f"测试类加载失败: {class_path} - {str(e)}")
            raise