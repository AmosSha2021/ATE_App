import unittest
from unittest.mock import patch
from core.dut.dut_manager import DUTManager
import yaml
from pathlib import Path  # 用于路径处理（可选）

class TestDUTSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 读取YAML配置文件
        with open("config/test_cases.yaml", encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 获取DUT配置节点
        dut_config = config['test_cases']['dut']
        
        # 构建完整telnet配置
        cls.telnet_config = {
            'type': dut_config['type'],
            'config': {
                'host': dut_config['config']['host'],
                'port': dut_config['config']['port'],
                'timeout': 5,  # 测试专用超时
                'username': dut_config['config']['username'],
                'password': dut_config['config']['password'],
                'login_prompts': dut_config['config'].get('login_prompts'),
                'password_prompts': dut_config['config'].get('password_prompts')
            }
        }

    def test_connection_flow(self):
        """测试完整的连接-命令-断开流程"""
        print(self.telnet_config)
        dut = DUTManager.create_dut(self.telnet_config)
        
        with patch('telnetlib.Telnet') as mock_telnet:
            # 添加分阶段模拟
            mock_instance = mock_telnet.return_value
            mock_instance.read_until.side_effect = [
                b"Login: ",      # 第一阶段返回登录提示
                b"Password: ",   # 第二阶段返回密码提示
                b"#"             # 最后返回命令提示符
            ]
            
            dut.connect()
            self.assertTrue(dut.is_connected)
            
            # # 恢复以下被注释的测试代码
            # response = dut.send_recv_command("test")
            # self.assertEqual(response, "TEST OK")
            
            # dut.disconnect()
            # self.assertFalse(dut.is_connected)

    # def test_invalid_command(self):
    #     """测试异常命令处理"""
    #     dut = DUTManager.create_dut(self.telnet_config)
        
    #     with patch('telnetlib.Telnet') as mock_telnet:
    #         mock_telnet.return_value.write.side_effect = Exception("Write failed")
    #         with self.assertRaises(Exception):
    #             dut.send_recv_command("invalid")

    # def test_invalid_dut_type(self):
    #     """测试无效DUT类型处理"""
    #     with self.assertRaises(ValueError):
    #         DUTManager.create_dut({'type': 'invalid', 'config': {}})

    # def test_custom_prompts(self):
    #     """测试自定义提示符配置"""
    #     custom_config = {
    #         'type': 'telnet',
    #         'config': {
    #             **self.telnet_config['config'],
    #             'login_prompts': ['user', 'login'],
    #             'password_prompts': ['passcode']
    #         }
    #     }
        
    #     with patch('telnetlib.Telnet') as mock_telnet:
    #         mock_telnet.return_value.read_very_eager.side_effect = [
    #             b"User Name:", 
    #             b"Enter Passcode:"
    #         ]
    #         dut = DUTManager.create_dut(custom_config)
    #         dut.connect()
    #         self.assertTrue(dut.is_connected)

    # def test_case_insensitive_login(self):
    #     """测试大小写不敏感的提示符匹配"""
    #     with patch('telnetlib.Telnet') as mock_telnet:
    #         mock_telnet.return_value.read_very_eager.side_effect = [
    #             b"LOGIN:",
    #             b"PASSWORD:"
    #         ]
    #         dut = DUTManager.create_dut(self.telnet_config)
    #         dut.connect()
    #         self.assertTrue(dut.is_connected)

    # def test_auth_failure(self):
    #     """测试认证失败场景"""
    #     with patch('telnetlib.Telnet') as mock_telnet:
    #         mock_telnet.return_value.read_until.return_value = b"Login incorrect"
    #         dut = DUTManager.create_dut(self.telnet_config)
    #         with self.assertRaises(ConnectionError):
    #             dut.connect()

    # def test_logging_output(self):
    #     """测试日志输出完整性"""
    #     with patch('telnetlib.Telnet'), \
    #         self.assertLogs(level='INFO') as log_context:
            
    #         dut = DUTManager.create_dut(self.telnet_config)
    #         dut.connect()
            
    #         logs = "\n".join(log_context.output)
    #         self.assertIn("正在连接 localhost", logs)
    #         self.assertIn("已发送用户名: admin", logs)
    #         self.assertIn("成功登录 localhost", logs)

if __name__ == '__main__':
    unittest.main()
