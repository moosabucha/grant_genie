from flask import Flask
from flask_login import LoginManager
from config import Config
import os

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from models.user import db, User
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access Grant Genie.'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.app_context():
        db.create_all()

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.export import export_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(export_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)