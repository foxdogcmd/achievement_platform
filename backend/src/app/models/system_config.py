from app import db
from datetime import datetime
import json
from sqlalchemy.orm import Mapped

class SystemConfig(db.Model):
    """系统配置模型"""
    __tablename__ = 'system_configs'

    config_id: Mapped[int] = db.Column(db.Integer, primary_key=True)
    config_key: Mapped[str] = db.Column(db.String(100), unique=True, nullable=False, comment='配置键')
    config_value: Mapped[str] = db.Column(db.Text, nullable=False, comment='配置值(JSON格式)')
    description: Mapped[str] = db.Column(db.String(200), comment='配置描述')
    created_at: Mapped[datetime] = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at: Mapped[datetime] = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __init__(self, config_key, config_value, description):
        self.config_key = config_key
        self.config_value = json.dumps(config_value, ensure_ascii=False) if isinstance(config_value, (dict, list)) else str(config_value)
        self.description = description
    
    def get_value(self):
        """获取配置值"""
        try:
            return json.loads(self.config_value)
        except (json.JSONDecodeError, TypeError):
            return self.config_value
    
    def set_value(self, value):
        """设置配置值"""
        self.config_value = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'config_id': self.config_id,
            'config_key': self.config_key,
            'config_value': self.get_value(),
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_config(key, default_value=None):
        """获取配置"""
        config = SystemConfig.query.filter_by(config_key=key).first()
        if config:
            return config.get_value()
        return default_value
    
    @staticmethod
    def set_config(key, value, description=None):
        """设置配置"""
        config = SystemConfig.query.filter_by(config_key=key).first()
        if config:
            config.set_value(value)
        else:
            config = SystemConfig(key, value, description)
            db.session.add(config)
        db.session.commit()
        return config
    
    @staticmethod
    def get_all_configs():
        """获取所有配置"""
        configs = SystemConfig.query.all()
        result = {}
        for config in configs:
            result[config.config_key] = config.get_value()
        return result
    
    @staticmethod
    def init_default_configs():
        """初始化默认配置"""
        default_configs = {
            'system_name': {
                'value': '学生成果登记与管理系统',
                'description': '系统名称'
            },
            'max_file_size': {
                'value': 10,
                'description': '文件上传大小限制(MB)'
            },
            'achievement_types': {
                'value': [
                    {'value': 'paper', 'label': '论文'},
                    {'value': 'competition', 'label': '竞赛'},
                    {'value': 'project', 'label': '项目'},
                    {'value': 'honor', 'label': '荣誉'}
                ],
                'description': '成果类型配置'
            },
            'achievement_levels': {
                'value': [
                    {'value': 'school', 'label': '校级'},
                    {'value': 'province', 'label': '省级'},
                    {'value': 'national', 'label': '国家级'}
                ],
                'description': '获奖级别配置'
            },
            'default_password': {
                'value': 'student123',
                'description': '新用户默认密码'
            }
        }
        
        for key, config_data in default_configs.items():
            existing = SystemConfig.query.filter_by(config_key=key).first()
            if not existing:
                SystemConfig.set_config(key, config_data['value'], config_data['description'])
    
    def __repr__(self):
        return f'<SystemConfig {self.config_key}>'