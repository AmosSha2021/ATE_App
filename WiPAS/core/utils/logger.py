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

# -*- coding: utf-8 -*-
"""
@Time: 2025/3/7 22:03
@Auth: shahao(Amos-Sha)
@File: logger.py
@IDE:  PyCharm
"""
import os
import re
import logging
import threading
from datetime import datetime
from pathlib import Path

class TestLogger:
    '''
    1: 单例模式：通过类变量+线程锁确保全局唯一实例
    2: 路径安全：自动处理路径格式和非法字符
    3: 异常处理：明确提示文件系统错误类型
    4: 双输出：  文件（带时间戳）和控制台实时输出
    5: 资源管理: 显式关闭旧文件handler防止泄漏
    '''
    """增强型线程安全日志系统"""
    _lock = threading.Lock()     # 线程安全锁，确保单例模式线程安全
    _instance = None             # 存储单例实例
    
    def __init__(self, log_dir: str, dut_name: str):
        """初始化日志系统核心参数"""
        # 路径安全处理：展开用户目录，转换为绝对路径
        self.log_dir = str(Path(os.path.expanduser(log_dir)).absolute())
        # 设备名安全处理：过滤非法文件名字符
        self.dut_name = re.sub(r'[\\/:*?"<>|]', '_', dut_name.strip())
        
        try:
            # 递归创建日志目录（存在则忽略）
            Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise RuntimeError(f"日志目录创建权限不足: {self.log_dir}") from e
        except OSError as e:
            raise RuntimeError(f"日志目录创建失败: {e}") from e
        
        # 配置日志处理器
        self._setup_logger()

    @classmethod
    def initialize(cls, log_dir: str, dut_name: str):
        """初始化单例实例（线程安全）"""
        with cls._lock:  # 通过线程锁确保初始化过程原子性
            if cls._instance is None:
                cls._instance = cls(log_dir, dut_name)

    @classmethod
    def get_instance(cls) -> 'TestLogger':
        """获取已初始化的单例实例"""
        if cls._instance is None:
            raise RuntimeError("请先调用initialize()进行初始化")
        return cls._instance

    def _new_file_handler(self) -> logging.FileHandler:
        """创建带时间戳的新日志文件处理器"""
        # 生成精确到毫秒的时间戳（示例：20240315_143022_123）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        
        # 构建安全日志路径
        log_file = Path(self.log_dir) / f"{self.dut_name}_{timestamp}.log"
        
        try:
            # 创建UTF-8编码的文件处理器
            handler = logging.FileHandler(log_file, encoding='utf-8')
        except PermissionError as e:
            raise RuntimeError(f"无文件写入权限: {log_file}") from e
        except OSError as e:
            raise RuntimeError(f"文件创建失败: {e}") from e
        
        # 应用统一格式
        handler.setFormatter(self._get_formatter())
        return handler

    def _get_formatter(self) -> logging.Formatter:
        """定义标准化日志格式"""
        return logging.Formatter(
            # 格式说明：
            # %(asctime)s.%(msecs)03d - 精确到毫秒的时间戳
            # %(levelname)-8s        - 左对齐的8字符日志级别
            # %(module)s.%(funcName)s - 模块名.函数名
            # %(message)s           - 日志消息
            fmt='%(asctime)s.%(msecs)03d | %(levelname)-8s | %(module)s.%(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'  # 日期格式（不含毫秒）
        )

    def _setup_logger(self):
        """配置日志系统核心组件"""
        # 获取/创建专用日志器
        self.logger = logging.getLogger("WiPAS")
        # 设置最低日志级别（DEBUG级别可捕获所有日志）
        self.logger.setLevel(logging.DEBUG)
        
        # 文件处理器（带时间戳的新文件）
        self.current_handler = self._new_file_handler()
        self.logger.addHandler(self.current_handler)
        
        # 控制台处理器（实时输出）
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._get_formatter())
        self.logger.addHandler(console_handler)

    def reset_for_new_test(self):
        """重置日志文件（测试用例切换时调用）"""
        # 移除旧处理器
        self.logger.removeHandler(self.current_handler)
        # 显式释放文件资源
        self.current_handler.close()
        # 创建新日志文件
        self.current_handler = self._new_file_handler()
        self.logger.addHandler(self.current_handler)

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """获取配置好的日志器"""
        return logging.getLogger("WiPAS")  # 返回初始化时创建的日志器