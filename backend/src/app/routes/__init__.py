from .auth import auth_bp
from .student import student_bp
from .leader import leader_bp
from .admin import admin_bp

__all__ = ['auth_bp', 'student_bp', 'leader_bp', 'admin_bp']