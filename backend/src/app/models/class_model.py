import uuid
from app import db
from datetime import datetime
from sqlalchemy.orm import Mapped

class Class(db.Model):
    """班级模型"""
    __tablename__ = 'classes'

    class_id: Mapped[str] = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    class_name: Mapped[str] = db.Column(db.String(50), nullable=False)
    college: Mapped[str] = db.Column(db.String(30), nullable=False)
    grade: Mapped[str] = db.Column(db.String(10), nullable=True)  # 年级
    major: Mapped[str] = db.Column(db.String(50), nullable=True)  # 专业
    created_at: Mapped[datetime] = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'class_id': self.class_id,
            'class_name': self.class_name,
            'college': self.college,
            'grade': self.grade,
            'major': self.major,
        }
    
    def __repr__(self):
        return f'<Class {self.class_name}>'

# ClassSchema 移到单独的文件中以避免循环依赖