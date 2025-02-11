from pathlib import Path

# 프로젝트 루트 디렉토리
BASE_DIR = Path(__file__).parent.parent.parent.absolute()

# 로그 디렉토리 설정
LOGS_DIR = BASE_DIR / 'logs'

# 로그 설정
LOG_CONFIG = {
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,   # 저장공간에 따라 갯수 확인 후 수정 가능 현재 테스트 단계는 5개의 파일만 보관
    'log_level': 'INFO', #'WARNING'
    'log_dir': LOGS_DIR
}