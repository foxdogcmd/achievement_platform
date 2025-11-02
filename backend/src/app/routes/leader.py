from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.achievement import Achievement
from app.models.audit_log import AuditLog
from app import db

leader_bp = Blueprint('leader', __name__)

@leader_bp.route('/pending-achievements', methods=['GET'])
@jwt_required()
def get_pending_achievements():
    """获取待审核的成果列表"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'team_leader':
            return jsonify({'message': '权限不足'}), 403
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 获取查询参数
        status = request.args.get('status')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 构建查询 - 获取分配给该队长的成果
        query = Achievement.query.filter_by(leader_id=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        else:
            # 如果没有指定状态，默认显示待审核的
            query = query.filter_by(status='pending')
        
        # 排序
        if sort_order == 'desc':
            query = query.order_by(getattr(Achievement, sort_by).desc())
        else:
            query = query.order_by(getattr(Achievement, sort_by))
        
        # 分页查询
        achievements = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 获取提交人信息
        achievement_list = []
        for achievement in achievements.items:
            achievement_dict = achievement.to_dict()
            submitter = User.query.get(achievement.submitter_id)
            achievement_dict['submitter_name'] = submitter.name if submitter else '未知'
            achievement_list.append(achievement_dict)
        
        return jsonify({
            'achievements': achievement_list,
            'total': achievements.total,
            'pages': achievements.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'获取待审核成果失败: {str(e)}'}), 500

@leader_bp.route('/achievements', methods=['GET'])
@jwt_required()
def get_all_achievements():
    """获取所有管理的成果"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'team_leader':
            return jsonify({'message': '权限不足'}), 403
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        type_filter = request.args.get('type')
        
        # 构建查询
        query = Achievement.query.filter_by(leader_id=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        if type_filter:
            query = query.filter_by(type=type_filter)
        
        # 分页查询
        achievements = query.order_by(Achievement.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 获取提交人信息
        achievement_list = []
        for achievement in achievements.items:
            achievement_dict = achievement.to_dict()
            submitter = User.query.get(achievement.submitter_id)
            achievement_dict['submitter_name'] = submitter.name if submitter else '未知'
            achievement_list.append(achievement_dict)
        
        return jsonify({
            'achievements': achievement_list,
            'total': achievements.total,
            'pages': achievements.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'获取成果列表失败: {str(e)}'}), 500

@leader_bp.route('/audit/<achievement_id>', methods=['POST'])
@jwt_required()
def audit_achievement(achievement_id):
    """审核成果"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'team_leader':
            return jsonify({'message': '权限不足'}), 403

        achievement: Achievement | None = Achievement.query.filter_by(
            achievement_id=achievement_id,
            leader_id=current_user_id
        ).first()
        
        if not achievement:
            return jsonify({'message': '成果不存在或无权限审核'}), 404
        assert isinstance(achievement, Achievement)
        if achievement.status != 'pending':
            return jsonify({'message': '该成果已被审核'}), 400
        
        data = request.get_json()
        action: str = data.get('action')  # approve, return, reject
        comment: str = data.get('comment', '')
        
        match action:
            case 'approve':
                achievement.status = action + 'd'
            case 'return' | 'reject':
                if not comment:
                    return jsonify({'message': '退回或拒绝必须填写审核意见'}), 400
                achievement.status = action + 'ed'
            case _:
                return jsonify({'message': '无效的审核操作'}), 400
        
        
        # 记录审核日志
        audit_log = AuditLog(
            achievement_id=achievement_id,
            auditor_id=current_user_id,
            action=action,
            comment=comment
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'message': '审核完成',
            'achievement': achievement.to_dict(),
            'audit_log': audit_log.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'审核失败: {str(e)}'}), 500

@leader_bp.route('/achievements/<achievement_id>', methods=['PUT'])
@jwt_required()
def update_achievement_info(achievement_id):
    """更新成果信息（队长权限）"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'team_leader':
            return jsonify({'message': '权限不足'}), 403
        
        achievement = Achievement.query.filter_by(
            achievement_id=achievement_id,
            leader_id=current_user_id
        ).first()
        
        if not achievement:
            return jsonify({'message': '成果不存在或无权限修改'}), 404
        
        data = request.get_json()
        
        # 队长可以修改的字段
        if 'level' in data:
            achievement.level = data['level']
        if 'remarks' in data:
            achievement.remarks = data['remarks']
        if 'is_public' in data:
            achievement.is_public = data['is_public']
        
        db.session.commit()
        
        return jsonify({
            'message': '成果信息更新成功',
            'achievement': achievement.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新成果信息失败: {str(e)}'}), 500

@leader_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """获取统计数据"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'team_leader':
            return jsonify({'message': '权限不足'}), 403
        
        # 统计各状态成果数量
        stats = {}
        stats['total'] = Achievement.query.filter_by(leader_id=current_user_id).count()
        stats['pending'] = Achievement.query.filter_by(leader_id=current_user_id, status='pending').count()
        stats['approved'] = Achievement.query.filter_by(leader_id=current_user_id, status='approved').count()
        stats['returned'] = Achievement.query.filter_by(leader_id=current_user_id, status='returned').count()
        stats['rejected'] = Achievement.query.filter_by(leader_id=current_user_id, status='rejected').count()
        
        # 按类型统计
        type_stats = db.session.query(
            Achievement.type,
            db.func.count(Achievement.achievement_id).label('count')
        ).filter_by(leader_id=current_user_id).group_by(Achievement.type).all()
        
        stats['by_type'] = {type_name: count for type_name, count in type_stats}
        
        # 按级别统计
        level_stats = db.session.query(
            Achievement.level,
            db.func.count(Achievement.achievement_id).label('count')
        ).filter_by(leader_id=current_user_id).group_by(Achievement.level).all()
        
        stats['by_level'] = {level_name: count for level_name, count in level_stats}
        
        return jsonify({'statistics': stats}), 200
        
    except Exception as e:
        return jsonify({'message': f'获取统计数据失败: {str(e)}'}), 500

@leader_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """获取审核记录"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'team_leader':
            return jsonify({'message': '权限不足'}), 403
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 查询审核记录
        logs = AuditLog.query.filter_by(auditor_id=current_user_id)\
            .order_by(AuditLog.audit_time.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        # 获取成果信息
        log_list = []
        for log in logs.items:
            log_dict = {
                'log_id': log.log_id,
                'achievement_id': log.achievement_id,
                'action': log.action,
                'comment': log.comment,
                'audit_time': log.audit_time.isoformat()
            }
            
            # 获取成果标题
            achievement = Achievement.query.get(log.achievement_id)
            log_dict['achievement_title'] = achievement.title if achievement else '已删除的成果'
            
            log_list.append(log_dict)
        
        return jsonify({
            'logs': log_list,
            'total': logs.total,
            'pages': logs.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'获取审核记录失败: {str(e)}'}), 500

@leader_bp.route('/team-achievements', methods=['GET'])
@jwt_required()
def get_team_achievements():
    """获取本队所有成果（别名接口）"""
    return get_all_achievements()

@leader_bp.route('/batch-operate', methods=['POST'])
@jwt_required()
def batch_operate_achievements():
    """批量操作成果"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'team_leader':
            return jsonify({'message': '权限不足'}), 403
        
        data = request.get_json()
        achievement_ids = data.get('achievement_ids', [])
        operation = data.get('operation')  # set_public, set_private
        value = data.get('value', True)
        
        if not achievement_ids:
            return jsonify({'message': '请选择要操作的成果'}), 400
        
        if operation not in ['set_public', 'set_private']:
            return jsonify({'message': '无效的操作类型'}), 400
        
        # 验证成果是否属于当前队长
        achievements = Achievement.query.filter(
            Achievement.achievement_id.in_(achievement_ids),
            Achievement.leader_id == current_user_id
        ).all()
        
        if len(achievements) != len(achievement_ids):
            return jsonify({'message': '部分成果不存在或无权限操作'}), 403
        
        # 执行批量操作
        for achievement in achievements:
            if operation == 'set_public':
                achievement.is_public = value
            elif operation == 'set_private':
                achievement.is_public = False
        
        db.session.commit()
        
        return jsonify({
            'message': f'批量操作成功，共处理 {len(achievements)} 个成果'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'批量操作失败: {str(e)}'}), 500

@leader_bp.route('/export', methods=['GET'])
@jwt_required()
def export_achievements():
    """导出成果报表"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.role != 'team_leader':
            return jsonify({'message': '权限不足'}), 403
        
        # 这里可以实现Excel导出功能
        # 暂时返回成功消息
        return jsonify({'message': '导出功能开发中'}), 200
        
    except Exception as e:
        return jsonify({'message': f'导出失败: {str(e)}'}), 500