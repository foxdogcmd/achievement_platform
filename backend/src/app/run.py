import os
from app import create_app, db
from app.models import User, Class, Achievement, AuditLog


def main():
    app = create_app(os.getenv('FLASK_ENV', 'development'))

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Class': Class,
            'Achievement': Achievement,
            'AuditLog': AuditLog,
        }

    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=int(os.getenv('PORT', '5000')))


if __name__ == "__main__":
    main()
