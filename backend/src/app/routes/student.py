from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models.user import User
from app.models import AuditLog, Achievement, Class
from app import db

student_bp = Blueprint('student', __name__)

@student_bp.route('/achievements', methods=['GET'])
@jwt_required()
def get_my_achievements():
    """获取我的成果列表"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'student':
            return jsonify({'message': '权限不足'}), 403
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        type_filter = request.args.get('type')
        
        # 构建查询
        query = Achievement.query.filter_by(submitter_id=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        if type_filter:
            query = query.filter_by(type=type_filter)
        
        # 分页查询
        achievements = query.order_by(Achievement.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'achievements': [
                {
                    **achievement.to_dict(),
                    'comment': (auditlog.comment if (auditlog := AuditLog.query.filter_by(achievement_id=achievement.achievement_id).first()) else ''),
                }
                for achievement in achievements.items
            ],
            'total': achievements.total,
            'pages': achievements.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'获取成果列表失败: {str(e)}'}), 500

@student_bp.route('/achievements', methods=['POST'])
@jwt_required()
def create_achievement():
    """创建成果"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'student':
            return jsonify({'message': '权限不足'}), 403
        
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['title', 'type', 'level', 'award_date', 'leader_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} 不能为空'}), 400
        
        # 验证队长是否存在
        leader = User.query.filter_by(user_id=data['leader_id'], role='team_leader').first()
        if not leader:
            return jsonify({'message': '指定的队长不存在'}), 400
        
        # 创建成果
        achievement = Achievement(
            title=data['title'],
            type=data['type'],
            level=data['level'],
            award_date=datetime.strptime(data['award_date'], '%Y-%m-%d').date() if isinstance(data['award_date'], str) else data['award_date'],
            supervisor=data.get('supervisor'),
            members=data.get('members'),
            class_id=user.class_id,
            leader_id=data['leader_id'],
            submitter_id=current_user_id,
            description=data.get('description'),
            evidence_files=data.get('evidence_files', [])
        )
        
        db.session.add(achievement)
        db.session.commit()
        
        return jsonify({
            'message': '成果创建成功',
            'achievement': achievement.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建成果失败: {str(e)}'}), 500

@student_bp.route('/achievements/<achievement_id>', methods=['PUT'])
@jwt_required()
def update_achievement(achievement_id):
    """更新成果"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'student':
            return jsonify({'message': '权限不足'}), 403
        
        achievement = Achievement.query.filter_by(
            achievement_id=achievement_id,
            submitter_id=current_user_id
        ).first()
        
        if not achievement:
            return jsonify({'message': '成果不存在'}), 404
        
        # 只有草稿或退回状态的成果可以修改
        if achievement.status not in ['pending', 'returned']:
            return jsonify({'message': '该成果当前状态不允许修改'}), 400
        
        data = request.get_json()
        
        # 更新字段
        if 'title' in data:
            achievement.title = data['title']
        if 'type' in data:
            achievement.type = data['type']
        if 'level' in data:
            achievement.level = data['level']
        if 'award_date' in data:
            achievement.award_date = datetime.strptime(data['award_date'], '%Y-%m-%d').date() if isinstance(data['award_date'], str) else data['award_date']
        if 'supervisor' in data:
            achievement.supervisor = data['supervisor']
        if 'leader_id' in data:
            # 验证队长是否存在
            leader = User.query.filter_by(user_id=data['leader_id'], role='team_leader').first()
            if leader:
                achievement.leader_id = data['leader_id']
            else:
                return jsonify({'message': '指定的队长不存在'}), 400
        if 'members' in data:
            achievement.members = data['members']
        if 'description' in data:
            achievement.description = data['description']
        if 'evidence_files' in data:
            achievement.evidence_files = data['evidence_files']
        
        # 如果是退回状态，重新提交时改为待审核
        if achievement.status == 'returned':
            achievement.status = 'pending'
        
        db.session.commit()
        
        return jsonify({
            'message': '成果更新成功',
            'achievement': achievement.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新成果失败: {str(e)}'}), 500

@student_bp.route('/achievements/<achievement_id>', methods=['DELETE'])
@jwt_required()
def delete_achievement(achievement_id):
    """删除成果"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'student':
            return jsonify({'message': '权限不足'}), 403
        
        achievement = Achievement.query.filter_by(
            achievement_id=achievement_id,
            submitter_id=current_user_id
        ).first()
        
        if not achievement:
            return jsonify({'message': '成果不存在'}), 404
        
        # 只有待审核状态的成果可以删除
        if achievement.status != 'pending':
            return jsonify({'message': '该成果当前状态不允许删除'}), 400
        
        db.session.delete(achievement)
        db.session.commit()
        
        return jsonify({'message': '成果删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除成果失败: {str(e)}'}), 500

@student_bp.route('/leaders', methods=['GET'])
@jwt_required()
def get_leaders():
    """获取队长列表"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'student':
            return jsonify({'message': '权限不足'}), 403
        
        leaders = User.query.filter_by(role='team_leader', is_active=True).all()
        
        return jsonify({
            'leaders': [{'user_id': leader.user_id, 'name': leader.name} for leader in leaders]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'获取队长列表失败: {str(e)}'}), 500

@student_bp.route('/classes', methods=['GET'])
@jwt_required()
def get_classes():
    """获取班级列表"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'student':
            return jsonify({'message': '权限不足'}), 403
        
        classes = Class.query.all()
        
        return jsonify({
            'classes': [cls.to_dict() for cls in classes]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'获取班级列表失败: {str(e)}'}), 500

@student_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """获取学生统计数据"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'student':
            return jsonify({'message': '权限不足'}), 403
        
        # 统计各状态成果数量
        stats = {}
        stats['total'] = Achievement.query.filter_by(submitter_id=current_user_id).count()
        stats['pending'] = Achievement.query.filter_by(submitter_id=current_user_id, status='pending').count()
        stats['approved'] = Achievement.query.filter_by(submitter_id=current_user_id, status='approved').count()
        stats['returned'] = Achievement.query.filter_by(submitter_id=current_user_id, status='returned').count()
        stats['rejected'] = Achievement.query.filter_by(submitter_id=current_user_id, status='rejected').count()
        
        # 按类型统计
        type_stats = db.session.query(
            Achievement.type,
            db.func.count(Achievement.achievement_id).label('count')
        ).filter_by(submitter_id=current_user_id).group_by(Achievement.type).all()
        
        stats['by_type'] = {type_name: count for type_name, count in type_stats}
        
        # 按级别统计
        level_stats = db.session.query(
            Achievement.level,
            db.func.count(Achievement.achievement_id).label('count')
        ).filter_by(submitter_id=current_user_id).group_by(Achievement.level).all()
        
        stats['by_level'] = {level_name: count for level_name, count in level_stats}
        
        return jsonify({'statistics': stats}), 200
        
    except Exception as e:
        return jsonify({'message': f'获取统计数据失败: {str(e)}'}), 500