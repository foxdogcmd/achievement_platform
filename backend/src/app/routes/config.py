from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from ..models.system_config import SystemConfig
from .. import db

config_bp = Blueprint('config', __name__)

@config_bp.route('/config', methods=['GET'])
@jwt_required()
def get_system_config():
    """获取系统配置 - 所有用户都可以访问"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        # 确保默认配置已初始化
        SystemConfig.init_default_configs()
        
        # 从数据库获取配置
        config = {
            'system_name': SystemConfig.get_config('system_name', '学生成果登记与管理系统'),
            'max_file_size': SystemConfig.get_config('max_file_size', 10),
            'achievement_types': SystemConfig.get_config('achievement_types', [
                {'value': 'paper', 'label': '论文'},
                {'value': 'competition', 'label': '竞赛'},
                {'value': 'project', 'label': '项目'},
                {'value': 'honor', 'label': '荣誉'}
            ]),
            'achievement_levels': SystemConfig.get_config('achievement_levels', [
                {'value': 'school', 'label': '校级'},
                {'value': 'province', 'label': '省级'},
                {'value': 'national', 'label': '国家级'}
            ]),
            'default_password': SystemConfig.get_config('default_password', 'student123')
        }
        
        return jsonify({'config': config}), 200
        
    except Exception as e:
        return jsonify({'message': f'获取系统配置失败: {str(e)}'}), 500

@config_bp.route('/config', methods=['PUT'])
@jwt_required()
def update_system_config():
    """更新系统配置 - 仅管理员可以访问"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        data = request.get_json()
        
        # 保存配置到数据库
        if 'system_name' in data:
            SystemConfig.set_config('system_name', data['system_name'], '系统名称')
        
        if 'max_file_size' in data:
            SystemConfig.set_config('max_file_size', data['max_file_size'], '文件上传大小限制(MB)')
        
        if 'achievement_types' in data:
            SystemConfig.set_config('achievement_types', data['achievement_types'], '成果类型配置')
        
        if 'achievement_levels' in data:
            SystemConfig.set_config('achievement_levels', data['achievement_levels'], '获奖级别配置')
        
        if 'default_password' in data:
            SystemConfig.set_config('default_password', data['default_password'], '新用户默认密码')
        
        return jsonify({'message': '系统配置保存成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'保存系统配置失败: {str(e)}'}), 500