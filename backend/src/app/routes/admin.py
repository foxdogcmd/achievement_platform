from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.user import User
from ..models.achievement import Achievement
from ..models.class_model import Class
from .. import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """获取用户列表"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        role = request.args.get('role')
        class_id = request.args.get('class_id')
        keyword = request.args.get('keyword')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 构建查询
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        if class_id:
            query = query.filter_by(class_id=class_id)
        if keyword:
            query = query.filter(
                db.or_(
                    User.username.contains(keyword),
                    User.name.contains(keyword)
                )
            )
        
        # 排序
        if sort_order == 'desc':
            query = query.order_by(getattr(User, sort_by).desc())
        else:
            query = query.order_by(getattr(User, sort_by))
        
        # 分页查询
        users = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 获取用户信息（包含班级名称）
        user_list = []
        for user_item in users.items:
            user_dict = user_item.to_dict()
            if user_item.class_id:
                class_info = Class.query.get(user_item.class_id)
                user_dict['class_name'] = class_info.class_name if class_info else '未知班级'
            else:
                user_dict['class_name'] = '无'
            user_list.append(user_dict)
        
        return jsonify({
            'users': user_list,
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'获取用户列表失败: {str(e)}'}), 500

@admin_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """更新用户信息"""
    try:
        current_user_id = get_jwt_identity()
        admin_user = User.query.get(current_user_id)
        
        if not admin_user or admin_user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'name' in data:
            user.name = data['name']
        if 'role' in data:
            user.role = data['role']
        if 'class_id' in data:
            user.class_id = data['class_id']
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': '用户信息更新成功',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新用户信息失败: {str(e)}'}), 500

@admin_bp.route('/classes', methods=['GET'])
@jwt_required()
def get_classes():
    """获取班级列表"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        classes = Class.query.all()
        return jsonify({
            'classes': [cls.to_dict() for cls in classes]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'获取班级列表失败: {str(e)}'}), 500

@admin_bp.route('/classes', methods=['POST'])
@jwt_required()
def create_class():
    """创建班级"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('class_name') or not data.get('college'):
            return jsonify({'message': '班级名称和学院不能为空'}), 400
        
        # 创建班级
        class_obj = Class(
            class_name=data['class_name'],
            college=data['college'],
            grade=data.get('grade'),
            major=data.get('major')
        )
        
        db.session.add(class_obj)
        db.session.commit()
        
        return jsonify({
            'message': '班级创建成功',
            'class': class_obj.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建班级失败: {str(e)}'}), 500

@admin_bp.route('/classes/<class_id>', methods=['PUT'])
@jwt_required()
def update_class(class_id):
    """更新班级信息"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        cls = Class.query.get(class_id)
        if not cls:
            return jsonify({'message': '班级不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'class_name' in data:
            cls.class_name = data['class_name']
        if 'college' in data:
            cls.college = data['college']
        
        db.session.commit()
        
        return jsonify({
            'message': '班级更新成功',
            'class': cls.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新班级失败: {str(e)}'}), 500

@admin_bp.route('/classes/<class_id>', methods=['DELETE'])
@jwt_required()
def delete_class(class_id):
    """删除班级"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        cls = Class.query.get(class_id)
        if not cls:
            return jsonify({'message': '班级不存在'}), 404
        
        # 检查是否有用户关联到该班级
        user_count = User.query.filter_by(class_id=class_id).count()
        if user_count > 0:
            return jsonify({'message': f'该班级还有 {user_count} 个用户，无法删除'}), 400
        
        db.session.delete(cls)
        db.session.commit()
        
        return jsonify({'message': '班级删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除班级失败: {str(e)}'}), 500

@admin_bp.route('/achievements', methods=['GET'])
@jwt_required()
def get_all_achievements():
    """获取所有成果"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        type_filter = request.args.get('type')
        level = request.args.get('level')
        
        # 构建查询
        query = Achievement.query
        
        if status:
            query = query.filter_by(status=status)
        if type_filter:
            query = query.filter_by(type=type_filter)
        if level:
            query = query.filter_by(level=level)
        
        # 分页查询
        achievements = query.order_by(Achievement.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'achievements': [achievement.to_dict() for achievement in achievements.items],
            'total': achievements.total,
            'pages': achievements.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'获取成果列表失败: {str(e)}'}), 500

@admin_bp.route('/achievements/<achievement_id>/public', methods=['PUT'])
@jwt_required()
def update_achievement_public(achievement_id):
    """更新成果公开状态"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        achievement = Achievement.query.get(achievement_id)
        if not achievement:
            return jsonify({'message': '成果不存在'}), 404
        
        data = request.get_json()
        achievement.is_public = data.get('is_public', False)
        
        db.session.commit()
        
        return jsonify({'message': '公开状态更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新失败: {str(e)}'}), 500

@admin_bp.route('/achievements/batch', methods=['POST'])
@jwt_required()
def batch_operate_achievements():
    """批量操作成果"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        data = request.get_json()
        achievement_ids = data.get('achievement_ids', [])
        operation = data.get('operation')
        value = data.get('value', True)
        
        if not achievement_ids:
            return jsonify({'message': '请选择要操作的成果'}), 400
        
        # 获取成果
        achievements = Achievement.query.filter(
            Achievement.achievement_id.in_(achievement_ids)
        ).all()
        
        # 执行批量操作
        for achievement in achievements:
            if operation == 'set_public':
                achievement.is_public = value
        
        db.session.commit()
        
        return jsonify({
            'message': f'批量操作成功，共处理 {len(achievements)} 个成果'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'批量操作失败: {str(e)}'}), 500

@admin_bp.route('/export', methods=['GET'])
@jwt_required()
def export_data():
    """导出数据"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        # 这里可以实现Excel导出功能
        # 暂时返回成功消息
        return jsonify({'message': '导出功能开发中'}), 200
        
    except Exception as e:
        return jsonify({'message': f'导出失败: {str(e)}'}), 500

@admin_bp.route('/config', methods=['GET'])
@jwt_required()
def get_system_config():
    """获取系统配置"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        # 返回默认系统配置
        config = {
            'system_name': '学生成果登记与管理系统',
            'max_file_size': 10,
            'achievement_types': [
                {'value': 'paper', 'label': '论文'},
                {'value': 'competition', 'label': '竞赛'},
                {'value': 'project', 'label': '项目'},
                {'value': 'honor', 'label': '荣誉'}
            ],
            'achievement_levels': [
                {'value': 'school', 'label': '校级'},
                {'value': 'province', 'label': '省级'},
                {'value': 'national', 'label': '国家级'}
            ],
            'default_password': 'student123'
        }
        
        return jsonify({'config': config}), 200
        
    except Exception as e:
        return jsonify({'message': f'获取系统配置失败: {str(e)}'}), 500

@admin_bp.route('/config', methods=['PUT'])
@jwt_required()
def update_system_config():
    """更新系统配置"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        data = request.get_json()
        
        # 这里可以将配置保存到数据库或配置文件
        # 暂时返回成功消息
        return jsonify({'message': '系统配置保存成功'}), 200
        
    except Exception as e:
        return jsonify({'message': f'保存系统配置失败: {str(e)}'}), 500

@admin_bp.route('/statistics/overview', methods=['GET'])
@jwt_required()
def get_overview_statistics():
    """获取系统概览统计"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        stats = {}
        
        # 用户统计
        stats['users'] = {
            'total': User.query.count(),
            'students': User.query.filter_by(role='student').count(),
            'leaders': User.query.filter_by(role='team_leader').count(),
            'admins': User.query.filter_by(role='admin').count()
        }
        
        # 成果统计
        stats['achievements'] = {
            'total': Achievement.query.count(),
            'pending': Achievement.query.filter_by(status='pending').count(),
            'approved': Achievement.query.filter_by(status='approved').count(),
            'returned': Achievement.query.filter_by(status='returned').count(),
            'rejected': Achievement.query.filter_by(status='rejected').count()
        }
        
        # 按类型统计成果
        type_stats = db.session.query(
            Achievement.type,
            db.func.count(Achievement.achievement_id).label('count')
        ).group_by(Achievement.type).all()
        
        stats['achievements']['by_type'] = {type_name: count for type_name, count in type_stats}
        
        # 按级别统计成果
        level_stats = db.session.query(
            Achievement.level,
            db.func.count(Achievement.achievement_id).label('count')
        ).group_by(Achievement.level).all()
        
        stats['achievements']['by_level'] = {level_name: count for level_name, count in level_stats}
        
        # 班级统计
        stats['classes'] = {
            'total': Class.query.count()
        }
        
        return jsonify({'statistics': stats}), 200
        
    except Exception as e:
        return jsonify({'message': f'获取统计数据失败: {str(e)}'}), 500

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    """创建用户"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['username', 'name', 'role', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} 不能为空'}), 400
        
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({'message': '用户名已存在'}), 400
        
        # 创建用户
        new_user = User(
            username=data['username'],
            name=data['name'],
            role=data['role'],
            class_id=data.get('class_id'),
            is_active=data.get('is_active', True)
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': '用户创建成功',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建用户失败: {str(e)}'}), 500

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """删除用户"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': '用户不存在'}), 404
        
        # 不能删除管理员账户
        if user.role == 'admin':
            return jsonify({'message': '不能删除管理员账户'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': '用户删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除用户失败: {str(e)}'}), 500

@admin_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_admin_statistics():
    """获取管理员统计数据"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'message': '权限不足'}), 403
        
        # 统计数据
        stats = {}
        stats['total_users'] = User.query.count()
        stats['total_achievements'] = Achievement.query.count()
        stats['total_classes'] = Class.query.count()
        stats['pending_achievements'] = Achievement.query.filter_by(status='pending').count()
        
        # 按角色统计用户
        role_stats = db.session.query(
            User.role,
            db.func.count(User.user_id).label('count')
        ).group_by(User.role).all()
        
        stats['by_role'] = {role: count for role, count in role_stats}
        
        # 按状态统计成果
        status_stats = db.session.query(
            Achievement.status,
            db.func.count(Achievement.achievement_id).label('count')
        ).group_by(Achievement.status).all()
        
        stats['by_status'] = {status: count for status, count in status_stats}
        
        return jsonify({'statistics': stats}), 200
        
    except Exception as e:
        return jsonify({'message': f'获取统计数据失败: {str(e)}'}), 500