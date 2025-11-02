import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from sqlalchemy.orm import Mapped

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    user_id: Mapped[str] = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = db.Column(db.String(255), nullable=False)
    role: Mapped[str] = db.Column(db.Enum('student', 'team_leader', 'admin', name='user_roles'), nullable=False)
    name: Mapped[str] = db.Column(db.String(50), nullable=False)
    class_id: Mapped[str] = db.Column(db.String(36), db.ForeignKey('classes.class_id'), nullable=True)
    created_at: Mapped[datetime] = db.Column(db.DateTime, default=datetime.now)
    is_active: Mapped[bool] = db.Column(db.Boolean, default=True)

    # 关系
    class_info = db.relationship('Class', backref='students', lazy=True)
    achievements = db.relationship('Achievement', foreign_keys='Achievement.leader_id', 
                                 backref='leader', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='auditor', lazy='dynamic')
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role,
            'name': self.name,
            'class_id': self.class_id,
            'class_name': self.class_info.class_name if self.class_info else None,
            'college': self.class_info.college if self.class_info else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

# UserSchema 移到单独的文件中以避免循环依赖