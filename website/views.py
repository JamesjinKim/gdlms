from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask_socketio import SocketIO
import logging
from . import socketio  # __init__.py에서 생성된 socketio 객체 import

# Blueprint 생성
views = Blueprint('views', __name__)

def init_views(app):
    """
    views Blueprint와 웹소켓을 초기화하는 함수
    Args:
        app: Flask 애플리케이션 인스턴스
    """
    # Blueprint 등록
    app.register_blueprint(views)
    
    # SocketIO 초기화
    socketio.init_app(app)

# 메인 페이지 라우트
@views.route('/', methods=['GET', 'POST'])
@login_required  # 로그인한 사용자만 접근 가능
def home():
    """메인 홈페이지 렌더링"""
    return render_template("home.html", user=current_user)

# 웹소켓 이벤트 핸들러들
@socketio.on('connect')
def handle_connect():
    """클라이언트 연결 시 호출"""
    if current_user.is_authenticated:
        logging.info(f"Web Client Connected: {current_user.email}")
        socketio.emit('server_info', {
            'status': 'connected',
            'user': current_user.email,
            'authority': current_user.authority
        })

@socketio.on('disconnect')
def handle_disconnect():
    """클라이언트 연결 해제 시 호출"""
    if current_user.is_authenticated:
        logging.info(f"Web Client Disconnected: {current_user.email}")
        socketio.emit('server_info', {
            'status': 'disconnected',
            'user': current_user.email
        })