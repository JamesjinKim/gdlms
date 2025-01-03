from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"
socketio = None

def create_app():
    global socketio
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'drjins7199!gdlms'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    # SocketIO 초기화
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # 데이터베이스 초기화
    db.init_app(app)

    # Blueprint 등록
    # Blueprint는 앱의 기능을 모듈화하는 방법
    from .views import views
    from .auth import auth
    
    # auth Blueprint 등록 (URL 접두사 '/')
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # 데이터베이스 모델 import
    from .models import User

    # 애플리케이션 컨텍스트 내에서 데이터베이스 테이블 생성
    with app.app_context():
        db.create_all()

    # Flask-Login 설정
    login_manager = LoginManager()  # LoginManager 인스턴스 생성
    login_manager.login_view = 'auth.login'  # 로그인이 필요할 때 리다이렉트할 뷰
    login_manager.init_app(app)  # LoginManager를 앱에 초기화

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Modbus 서버 초기화
    from .modbus_server import setup_modbus_server
    setup_modbus_server(app, socketio)

    return app, socketio  # socketio도 함께 반환

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')