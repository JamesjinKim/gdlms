# src/backend/common/db_base.py
class BaseDBHandler:
    """공통 DB 처리 기능"""
    # 기본 DB 연결 및 쿼리 기능 구현

# src/backend/stocker/stocker_db_handler.py
class StockerDBHandler(BaseDBHandler):
    """Stocker 전용 DB 처리"""
    # Stocker 데이터 저장 및 조회 기능 구현