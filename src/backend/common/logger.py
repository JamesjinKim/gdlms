import logging
from logging.handlers import RotatingFileHandler
import os
from backend.config import LOGS_DIR, LOG_CONFIG

def setup_logger(name, filename):
    # 로그 디렉토리 생성
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_CONFIG['log_level']))
    
    # 기존 핸들러 제거
    logger.handlers.clear()
    
    # 파일 핸들러 설정 (INFO 레벨)
    log_file = LOGS_DIR / filename
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=LOG_CONFIG['max_file_size'], 
        backupCount=LOG_CONFIG['backup_count']
    )
    file_handler.setLevel(logging.INFO)  # 파일에는 INFO 레벨부터 기록
    
    # 콘솔 핸들러 설정 (WARNING 레벨)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # 콘솔에는 WARNING 레벨부터 출력
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger