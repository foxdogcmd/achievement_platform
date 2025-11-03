from flask import Blueprint, jsonify, request
from sqlalchemy import func, extract
from ..models import Achievement, User, Class
from .. import db

public_bp = Blueprint('public', __name__, url_prefix='/api/public')

@public_bp.route('/achievements', methods=['GET'])
def get_public_achievements():
    """获取公开的成果列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        type_filter = request.args.get('type')
        level_filter = request.args.get('level')
        class_id = request.args.get('class_id')
        year = request.args.get('year', type=int)
        
        # 构建查询 - 只获取公开且已通过的成果
        query = Achievement.query.filter(
            Achievement.is_public == True,
            Achievement.status == 'approved'
        )
        
        # 应用筛选条件
        if type_filter:
            query = query.filter_by(type=type_filter)
        if level_filter:
            query = query.filter_by(level=level_filter)
        if class_id:
            query = query.filter_by(class_id=class_id)
        if year:
            query = query.filter(extract('year', Achievement.award_date) == year)
        
        # 分页查询
        achievements = query.order_by(Achievement.award_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 获取成果详细信息
        achievement_list = []
        for achievement in achievements.items:
            achievement_dict = achievement.to_dict()
            
            # 获取班级信息
            if achievement.class_id:
                class_info = Class.query.get(achievement.class_id)
                achievement_dict['class_name'] = class_info.class_name if class_info else '未知班级'
                achievement_dict['college'] = class_info.college if class_info else '未知学院'
            else:
                achievement_dict['class_name'] = '未知班级'
                achievement_dict['college'] = '未知学院'
            
            # 移除敏感信息
            achievement_dict.pop('submitter_id', None)
            achievement_dict.pop('leader_id', None)
            achievement_dict.pop('evidence_files', None)  # 公开展示不显示佐证材料
            
            achievement_list.append(achievement_dict)
        
        return jsonify({
            'achievements': achievement_list,
            'total': achievements.total,
            'pages': achievements.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'获取公开成果失败: {str(e)}'}), 500

@public_bp.route('/statistics', methods=['GET'])
def get_public_statistics():
    """获取公开成果统计数据"""
    try:
        # 基础查询条件：公开且已通过的成果
        base_query = Achievement.query.filter(
            Achievement.is_public == True,
            Achievement.status == 'approved'
        )
        
        # 总数统计
        total_count = base_query.count()
        
        # 按类型统计
        type_stats = db.session.query(
            Achievement.type,
            func.count(Achievement.achievement_id).label('count')
        ).filter(
            Achievement.is_public == True,
            Achievement.status == 'approved'
        ).group_by(Achievement.type).all()
        
        # 按级别统计
        level_stats = db.session.query(
            Achievement.level,
            func.count(Achievement.achievement_id).label('count')
        ).filter(
            Achievement.is_public == True,
            Achievement.status == 'approved'
        ).group_by(Achievement.level).all()
        
        # 按年度统计
        year_stats = db.session.query(
            extract('year', Achievement.award_date).label('year'),
            func.count(Achievement.achievement_id).label('count')
        ).filter(
            Achievement.is_public == True,
            Achievement.status == 'approved'
        ).group_by(extract('year', Achievement.award_date)).order_by('year').all()
        
        # 按班级统计（前10名）
        class_stats = db.session.query(
            Class.class_name,
            Class.college,
            func.count(Achievement.achievement_id).label('count')
        ).join(Achievement, Achievement.class_id == Class.class_id)\
        .filter(
            Achievement.is_public == True,
            Achievement.status == 'approved'
        ).group_by(Class.class_id, Class.class_name, Class.college)\
        .order_by(func.count(Achievement.achievement_id).desc())\
        .limit(10).all()
        
        return jsonify({
            'total_count': total_count,
            'by_type': [{'type': type_name, 'count': count} for type_name, count in type_stats],
            'by_level': [{'level': level, 'count': count} for level, count in level_stats],
            'by_year': [{'year': int(year), 'count': count} for year, count in year_stats],
            'by_class': [{'class_name': class_name, 'college': college, 'count': count} 
                        for class_name, college, count in class_stats]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'获取统计数据失败: {str(e)}'}), 500

@public_bp.route('/classes', methods=['GET'])
def get_classes():
    """获取班级列表"""
    try:
        classes = Class.query.all()
        class_list = [{'class_id': cls.class_id, 'class_name': cls.class_name, 'college': cls.college} 
                     for cls in classes]
        
        return jsonify({'classes': class_list}), 200
        
    except Exception as e:
        return jsonify({'message': f'获取班级列表失败: {str(e)}'}), 500