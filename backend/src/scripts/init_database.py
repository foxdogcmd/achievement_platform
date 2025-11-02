#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表和初始数据
"""

from datetime import datetime

from app import create_app, db
from app.models import User, Class, Achievement, AuditLog
from app.models.system_config import SystemConfig

def main():
    """初始化数据库"""
    app = create_app('development')
    
    with app.app_context():
        # 删除所有表（谨慎使用）
        print("正在删除现有表...")
        db.drop_all()
        
        # 创建所有表
        print("正在创建数据库表...")
        db.create_all()
        
        # 创建初始数据
        print("正在创建初始数据...")
        create_initial_data()
        
        print("数据库初始化完成！")

def create_initial_data():
    """创建初始数据"""
    
    # 创建班级
    classes_data = [
        {'class_name': '2021级侦查学1班', 'college': '侦查学院', 'grade': '2021', 'major': '侦查学'},
        {'class_name': '2021级侦查学2班', 'college': '侦查学院', 'grade': '2021', 'major': '侦查学'},
        {'class_name': '2021级刑事科学技术1班', 'college': '侦查学院', 'grade': '2021', 'major': '刑事科学技术'},
        {'class_name': '2021级网络安全与执法1班', 'college': '信息网络安全学院', 'grade': '2021', 'major': '网络安全与执法'},
        {'class_name': '2022级侦查学1班', 'college': '侦查学院', 'grade': '2022', 'major': '侦查学'},
    ]
    
    classes = []
    for class_data in classes_data:
        class_obj = Class(**class_data)
        db.session.add(class_obj)
        classes.append(class_obj)
    
    db.session.flush()  # 获取class_id
    
    # 创建管理员
    admin = User(
        username='admin',
        name='系统管理员',
        role='admin'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # 创建队长
    leaders_data = [
        {'username': 'leader001', 'name': '张队长', 'password': 'leader123'},
        {'username': 'leader002', 'name': '李队长', 'password': 'leader123'},
        {'username': 'leader003', 'name': '王队长', 'password': 'leader123'},
    ]
    
    leaders = []
    for leader_data in leaders_data:
        leader = User(
            username=leader_data['username'],
            name=leader_data['name'],
            role='team_leader'
        )
        leader.set_password(leader_data['password'])
        db.session.add(leader)
        leaders.append(leader)
    
    db.session.flush()  # 获取leader_id
    
    # 创建学生
    students_data = [
        {'username': '2021001', 'name': '张三', 'class_idx': 0},
        {'username': '2021002', 'name': '李四', 'class_idx': 0},
        {'username': '2021003', 'name': '王五', 'class_idx': 1},
        {'username': '2021004', 'name': '赵六', 'class_idx': 1},
        {'username': '2021005', 'name': '钱七', 'class_idx': 2},
        {'username': '2022001', 'name': '孙八', 'class_idx': 4},
    ]
    
    students = []
    for student_data in students_data:
        student = User(
            username=student_data['username'],
            name=student_data['name'],
            role='student',
            class_id=classes[student_data['class_idx']].class_id
        )
        student.set_password('student123')
        db.session.add(student)
        students.append(student)
    
    db.session.flush()  # 获取student_id
    
    # 创建示例成果
    achievements_data = [
        {
            'title': '全国大学生数学建模竞赛一等奖',
            'type': 'competition',
            'level': 'national',
            'award_date': '2023-10-15',
            'supervisor': '张教授',
            'members': ['张三', '李四'],
            'submitter_idx': 0,
            'leader_idx': 0,
            'class_idx': 0,
            'status': 'approved'
        },
        {
            'title': '基于深度学习的图像识别算法研究',
            'type': 'paper',
            'level': 'province',
            'award_date': '2023-09-20',
            'supervisor': '李教授',
            'members': ['王五'],
            'submitter_idx': 2,
            'leader_idx': 1,
            'class_idx': 1,
            'status': 'pending'
        }
    ]
    
    for achievement_data in achievements_data:
        achievement = Achievement(
            title=achievement_data['title'],
            type=achievement_data['type'],
            level=achievement_data['level'],
            award_date=datetime.strptime(achievement_data['award_date'], '%Y-%m-%d').date(),
            supervisor=achievement_data['supervisor'],
            members=achievement_data['members'],
            submitter_id=students[achievement_data['submitter_idx']].user_id,
            leader_id=leaders[achievement_data['leader_idx']].user_id,
            class_id=classes[achievement_data['class_idx']].class_id,
            status=achievement_data['status']
        )
        db.session.add(achievement)
    
    # 提交所有更改
    db.session.commit()
    
    # 初始化系统配置
    print("正在初始化系统配置...")
    SystemConfig.init_default_configs()
    
    print(f"创建了 {len(classes)} 个班级")
    print(f"创建了 1 个管理员账户: admin/admin123")
    print(f"创建了 {len(leaders)} 个队长账户: leader001-003/leader123")
    print(f"创建了 {len(students)} 个学生账户: 学号/student123")
    print(f"创建了 {len(achievements_data)} 个示例成果")
    print("系统配置已初始化")

if __name__ == '__main__':
    main()