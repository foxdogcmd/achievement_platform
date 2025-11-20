import uuid
from datetime import datetime
from app import db
from app.models import User
from sqlalchemy.orm import Mapped

class AuditLog(db.Model):
    """审核日志模型"""
    __tablename__ = 'logs'
    
    log_id: Mapped[str] = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # 关联到成果：删除成果时级联删除对应审核日志
    achievement_id: Mapped[str] = db.Column(
        db.String(36),
        db.ForeignKey('achievements.achievement_id', ondelete='CASCADE'),
        nullable=False
    )
    # 关联到审核人：删除审核人时置空审核人字段
    auditor_id: Mapped[str] = db.Column(
        db.String(36),
        db.ForeignKey('users.user_id', ondelete='SET NULL'),
        nullable=True
    )
    action: Mapped[str] = db.Column(db.Enum('approve', 'return', 'reject', name='audit_actions'), nullable=False)
    comment: Mapped[str] = db.Column(db.Text, nullable=True)  # 审核意见
    audit_time: Mapped[datetime] = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'log_id': self.log_id,
            'achievement_id': self.achievement_id,
            'auditor_id': self.auditor_id,
            'auditor_name': auditor.name if (auditor:=User.query.get(self.auditor_id)) else None,
            'action': self.action,
            'action_display': self.action_display,
            'comment': self.comment,
            'audit_time': self.audit_time.isoformat() if self.audit_time else None
        }
    
    @property
    def action_display(self):
        """操作显示名称"""
        action_map = {
            'approve': '通过',
            'return': '退回',
            'reject': '拒绝'
        }
        return action_map.get(self.action, self.action)
    
    def __repr__(self):
        return f'<AuditLog {self.action} by \
            {auditor.name if (auditor:=User.query.get(self.auditor_id)) else "Unknown"}>'
