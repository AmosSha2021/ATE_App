# -*- coding: utf-8 -*-
"""
@Time ： 2025/3/8 8:56
@Auth ： shahao(Amos-Sha)
@File ：test_logger.py
@IDE ：PyCharm
"""
import unittest
import logging
import os
import shutil
import glob
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from core.utils.logger import TestLogger, get_logger


class TestLoggerSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_log_dir = os.path.abspath("test_logs")
        cls.dut_name = "TEST_DUT"

    def setUp(self):
        # 目录清理和重建
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
        os.makedirs(self.test_log_dir)

        # 重置单例和日志器
        TestLogger._instance = None
        logger = logging.getLogger("WiPAS")
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        logger.addHandler(logging.NullHandler())

    def tearDown(self):
        # 确保关闭所有日志处理器
        logger = logging.getLogger("WiPAS")
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                logger.removeHandler(handler)
                handler.close()

    def test_01_singleton_pattern(self):
        """测试单例模式有效性"""
        with self.assertRaises(RuntimeError):
            TestLogger.get_instance()

        logger1 = TestLogger.initialize(self.test_log_dir, self.dut_name)
        logger2 = TestLogger.initialize(self.test_log_dir, "NEW_DUT")
        self.assertIs(logger1, logger2)

    def test_02_log_file_creation(self):
        """测试日志文件生成"""
        TestLogger.initialize(self.test_log_dir, self.dut_name)
        logger = get_logger()

        test_msg = "TEST_FILE_CREATION"
        logger.info(test_msg)

        log_files = glob.glob(os.path.join(self.test_log_dir, f"*{self.dut_name}*"))
        self.assertTrue(len(log_files) > 0, "未找到DUT命名的日志文件")

    def test_03_log_format(self):
        """验证日志格式"""
        TestLogger.initialize(self.test_log_dir, self.dut_name)
        logger = get_logger()

        test_msg = f"TEST_FORMAT_{datetime.now().timestamp()}"
        logger.warning(test_msg)

        # 查找最新日志文件
        log_files = glob.glob(os.path.join(self.test_log_dir, f"*{self.dut_name}*"))
        latest_log = max(log_files, key=os.path.getctime)

        with open(latest_log, 'r', encoding='utf-8') as f:
            log_line = f.readline().strip()

        parts = log_line.split(" | ")
        try:
            self.assertEqual(parts[2], "test_logger.test_03_log_format",f"模块路径错误：{parts[2]}")
            datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S.%f')
            self.assertTrue(parts[1].startswith("WARNING"), f"日志级别错误：{parts[1]}")
            self.assertEqual(parts[2], "test_logger.TestLoggerSystem.test_03_log_format",
                             f"模块路径错误：{parts[2]}")
            self.assertEqual(parts[3], test_msg, "日志消息不匹配")
        except ValueError as e:
            self.fail(f"时间戳格式错误：{str(e)}")

    def test_04_multithread_logging(self):
        """测试多线程日志记录"""
        TestLogger.initialize(self.test_log_dir, self.dut_name)
        logger = get_logger()

        messages = [f"THREAD_{i}_{datetime.now().timestamp()}" for i in range(5)]

        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(lambda msg: logger.info(msg), messages)

        log_files = glob.glob(os.path.join(self.test_log_dir, f"*{self.dut_name}*"))
        latest_log = max(log_files, key=os.path.getctime)

        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = [line for line in f if "INFO" in line]

        self.assertEqual(len(lines), 5, f"找到{len(lines)}条INFO日志，预期5条")

    def test_05_error_logging(self):
        """测试异常记录"""
        TestLogger.initialize(self.test_log_dir, self.dut_name)
        logger = get_logger()

        try:
            1 / 0
        except ZeroDivisionError:
            logger.error("除零错误", exc_info=True)

        log_files = glob.glob(os.path.join(self.test_log_dir, f"*{self.dut_name}*"))
        latest_log = max(log_files, key=os.path.getctime)

        with open(latest_log, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("ZeroDivisionError", content)
        self.assertIn("Traceback (most recent call last)", content)


if __name__ == '__main__':
    unittest.main()