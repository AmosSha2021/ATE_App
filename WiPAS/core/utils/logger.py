# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 22:03
@Auth: shahao(Amos-Sha)
@File: logger.py
@IDE:  PyCharm
"""
import os
import logging
import threading
from datetime import datetime

class TestLogger:
    """
    1: 线程安全单例模式:通过类变量_instance和线程锁_lock确保全局唯一实例
    2: 动态文件名生成：文件名包含设备名和毫秒级时间戳(如ATE_Device_20240315_143022_123.log)
    3: 日志格式统一：精确到毫秒的时间戳+模块定位信息，便于调试
    4: 资源管理: 在reset_for_new_test()中显式关闭旧文件handler,避免文件句柄泄漏
    5: 双输出渠道：同时支持文件和控制台输出，且保持格式一致
    """
    _lock = threading.Lock()     # 线程安全锁，用于单例模式
    _instance = None             # 存储单例实例
    
    def __init__(self, log_dir: str, dut_name: str):
        # 初始化日志目录和设备名称
        self.log_dir = log_dir
        self.dut_name = dut_name
        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)
        # 配置日志系统
        self._setup_logger()

    @classmethod
    def initialize(cls, log_dir: str, dut_name: str):
        with cls._lock:  # 线程安全初始化
            if cls._instance is None:
                # 创建唯一实例
                cls._instance = cls(log_dir, dut_name)

    @classmethod
    def get_instance(cls) -> 'TestLogger':
        # 获取已初始化的实例
        if cls._instance is None:
            raise RuntimeError("需要先调用initialize()初始化")
        return cls._instance

    def _new_file_handler(self):
        """创建带时间戳的新日志文件处理器"""
        # 生成精确到毫秒的时间戳（最后3位）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        # 构建日志文件路径
        log_file = os.path.join(self.log_dir, f"{self.dut_name}_{timestamp}.log")
        # 创建文件处理器
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(self._get_formatter())
        return handler

    def _get_formatter(self):
        """定义统一日志格式"""
        return logging.Formatter(
            # 包含毫秒的时间戳 | 对齐的日志级别 | 模块.函数名 | 消息
            '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(module)s.%(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'  # 定义时间显示格式
        )

    def _setup_logger(self):
        """配置日志系统核心方法"""
        # 获取/创建名为"WiPAS"的日志器
        self.logger = logging.getLogger("WiPAS")
        # 设置最低日志级别
        self.logger.setLevel(logging.DEBUG)
        
        # 创建并添加文件处理器
        self.current_handler = self._new_file_handler()
        self.logger.addHandler(self.current_handler)
        
        # 创建并添加控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(console_handler)

    def reset_for_new_test(self):
        """测试用例重置方法"""
        # 移除旧的文件处理器
        self.logger.removeHandler(self.current_handler)
        # 关闭旧处理器释放资源
        self.current_handler.close()
        # 创建并添加新文件处理器
        self.current_handler = self._new_file_handler()
        self.logger.addHandler(self.current_handler)

def get_logger() -> logging.Logger:
    return TestLogger.get_instance().logger