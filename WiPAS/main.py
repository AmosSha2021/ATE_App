import logging.config
import yaml
from core.test_management.test_manager import TestManager


def main():
    # 初始化日志系统
    with open('config/logging.yaml') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

    # 启动测试管理
    test_manager = TestManager('config/test_cases.yaml')
    test_manager.run_test_sequence()


if __name__ == "__main__":
    main()