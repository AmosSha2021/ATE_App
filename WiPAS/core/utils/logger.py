# -*- coding: utf-8 -*-
"""
@Time ： 2025/3/7 22:29
@Auth ： shahao(Amos-Sha)
@File ：logger.py
@IDE ：PyCharm
"""
import os
import logging
import threading
from datetime import datetime
from typing import Optional


class TestLogger:
    _lock = threading.Lock()
    _instance: Optional['TestLogger'] = None
    current_handler: Optional[logging.Handler] = None

    def __init__(self, log_dir: str = "logs", dut_name: str = "UNKNOWN_DUT"):
        if TestLogger._instance is not None:
            raise RuntimeError("Use get_instance() method to get the singleton instance")

        self.log_dir = log_dir
        self.dut_name = dut_name
        self._setup_logger()

    @classmethod
    def initialize(cls, log_dir: str, dut_name: str) -> 'TestLogger':
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(log_dir, dut_name)
            return cls._instance

    @classmethod
    def get_instance(cls) -> 'TestLogger':
        if cls._instance is None:
            raise RuntimeError("Logger not initialized. Call initialize() first")
        return cls._instance

    def _new_file_handler(self):
        """创建新的文件处理器"""
        os.makedirs(self.log_dir, exist_ok=True)

        # 生成精确到毫秒的时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        log_file = os.path.join(
            self.log_dir,
            f"{self.dut_name}_{timestamp}.log"
        )

        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(module)s.%(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(formatter)
        return handler

    def _setup_logger(self):
        """配置日志系统"""
        self.logger = logging.getLogger("WiPAS")
        self.logger.setLevel(logging.DEBUG)

        # 新增文件处理器
        self.current_handler = self._new_file_handler()
        self.logger.addHandler(self.current_handler)

        # 控制台处理器检查逻辑优化
        console_handlers = [h for h in self.logger.handlers
                            if isinstance(h, logging.StreamHandler)]
        if not console_handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s.%(msecs)03d | %(levelname)-8s | %(module)s.%(funcName)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            self.logger.addHandler(console_handler)

    def reset_for_new_test(self):
        """开始新测试时调用"""
        with self._lock:
            # 关闭并移除旧的文件处理器
            if self.current_handler:
                self.logger.removeHandler(self.current_handler)
                self.current_handler.close()
            self._setup_logger()



# 全局访问快捷方式
def get_logger() -> logging.Logger:
    return TestLogger.get_instance().logger