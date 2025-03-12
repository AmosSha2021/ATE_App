# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 22:03
@Auth: shahao(Amos-Sha)
@File: test_manager.py
@IDE:  PyCharm
"""

from typing import List, Dict
import yaml
from core.utils.logger import TestLogger  # 替代原来的 get_logger
from core.instruments.instrument_manager import InstrumentManager
from core.dut.dut_manager import DUTManager
from pprint import pformat


class TestManager:
    def __init__(self, config_path: str):
        root_logger = TestLogger.get_logger()  # 通过类方法获取
        self.logger = root_logger.getChild("TestManager")
        self.config = self._load_config(config_path)
        self.test_cases = self._load_test_cases()
        self.dut_config = self.config.get('dut_config', {})  # 新增全局DUT配置
        self._test_ready = False

    def _load_config(self, config_path: str) -> dict:
        """统一加载配置文件"""
        try:
            self.logger.info(f"正在加载主配置文件: {config_path}")
            with open(config_path, encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error("主配置文件加载失败 | 路径: %s | 错误: %s", 
                             config_path, str(e), exc_info=True)
            return {}

    def _load_test_cases(self) -> List[Dict]:
        """从配置解析测试用例"""
        try:
            
            self.logger.debug("完整配置结构:\n%s", pformat(self.config))
            
            test_cases = self.config.get('test_cases', [])
            if isinstance(test_cases, dict):
                test_cases = [test_cases]
                
            self.logger.info("已加载 %d 个测试用例", len(test_cases))
            if test_cases:
                self.logger.info("测试用例列表: %s", 
                               [case.get('name', '未命名用例') for case in test_cases])
            return test_cases
            
        except Exception as e:
            self.logger.error("测试用例解析失败: %s", str(e), exc_info=True)
            return []

    def _pre_test_setup(self):
        """测试前准备"""
        self.logger.info("正在初始化测试环境...")
        self._test_ready = True
        self.logger.info("测试环境准备就绪")

    def _post_test_cleanup(self):
        """测试后清理"""
        self.logger.info("正在清理测试资源...")
        self._test_ready = False

    def run_test_sequence(self):
        """执行完整测试流程"""
        try:
            self.logger.info("..................................................开始执行测试流程..................................................")
            self._pre_test_setup()
            for case in self.test_cases:
                self._execute_test_case(case)
            self._post_test_cleanup()
        except Exception as e:
            self.logger.error(f"测试异常终止: {str(e)}")

    def _create_instrument(self, case_config: Dict):
        """创建仪器实例"""
        if 'instrument' not in case_config:
            self.logger.info("跳过仪器初始化")
            return None
            
        try:
            return InstrumentManager.create_instrument(
                instrument_type=case_config['instrument']['type'],
                config=case_config['instrument'].get('config', {}),
                logger=self.logger
            )
        except Exception as e:
            self.logger.error(f"仪器初始化失败: {str(e)}")
            return None

    def _create_dut(self):
        """从全局配置创建DUT实例"""
        if not self.dut_config:
            self.logger.info("未配置DUT，跳过初始化")
            return None
            
        try:
            self.logger.debug("check dut_config:\n%s", pformat(self.dut_config))
            self.logger.info("self.dut_config.get('config') type: %s", type(self.dut_config))
            return DUTManager().create_dut(dut_config=self.dut_config)
        
        except Exception as e:
            self.logger.error(f"DUT初始化失败: {str(e)}")
            return None

    def _execute_test_case(self, case_config: Dict):
        """执行单个测试用例"""
        dut_manager = None
        instrument = None
        
        try:
            test_class = self._load_test_class(case_config['test_class'])
            self.logger.info(f"开始执行测试用例: {case_config.get('name', '未命名用例')}")
            
            # 初始化设备
            instrument = self._create_instrument(case_config)
            dut_manager = self._create_dut()  # 使用全局配置初始化DUT

            test_params = {
                'config': case_config,
                'dut_manager': dut_manager,
                'instrument': instrument
            }
            
            test_case = test_class(**test_params)
            test_case.run()
            
        except KeyError as e:
            self.logger.error(f"测试配置错误: 缺少必要字段 {str(e)}")
        except Exception as e:
            self.logger.error(f"测试执行异常: {str(e)}")
        finally:
            if dut_manager and hasattr(dut_manager, 'disconnect'):
                dut_manager.disconnect()
            if instrument and hasattr(instrument, 'disconnect'):
                instrument.disconnect()

    def _load_test_class(self, class_path: str):
        """动态加载测试类"""
        from importlib import import_module
        module_path, class_name = class_path.rsplit('.', 1)
        try:
            module = import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            self.logger.error(f"测试类加载失败: {class_path} - {str(e)}")
            raise