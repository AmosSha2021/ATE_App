# -*- coding: utf-8 -*-
"""
@Time : 2025/3/7 22:05
@Auth : shahao(Amos-Sha)
@File : instrument_manager.py
@IDE :  PyCharm
"""

from importlib import import_module
from typing import Dict, Any

class InstrumentManager:
    """统一仪器管理类"""
    
    _instrument_registry = {
        'gpon': ('core.instruments.gpon_instrument', 'GPonInstrument'),
        'rf': ('core.instruments.rf_instrument', 'RFInstrument')
    }
    
    @classmethod
    def create_instrument(cls, 
                         instrument_type: str, 
                         config: Dict[str, Any],
                         logger) -> Any:
        """创建仪器实例"""
        if instrument_type not in cls._instrument_registry:
            raise ValueError(f"未知仪器类型: {instrument_type}")
            
        module_path, class_name = cls._instrument_registry[instrument_type]
        
        try:
            module = import_module(module_path)
            instrument_class = getattr(module, class_name)
            instance = instrument_class()
            instance.logger = logger.getChild(class_name)
            instance.connect(**config)  # 传递仪器配置参数
            return instance
        except Exception as e:
            logger.error(f"仪器初始化失败: {str(e)}")
            raise