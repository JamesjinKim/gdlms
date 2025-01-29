# src/backend/common/init_db.py
import sqlite3
import os
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

def init_operational_db():
   """운영 DB 초기화 및 테이블 생성
   - 사용자 관리
   - 설비 마스터 데이터 관리"""
   
   # DB 파일 경로 설정
   db_dir = Path("src/data/db/operational")   
   # DB 디렉토리가 없으면 생성
   db_dir.mkdir(parents=True, exist_ok=True)
   db_path = db_dir / "operational.db"
   
   conn = None
   try:
       conn = sqlite3.connect(db_path)
       cursor = conn.cursor()

       # 사용자 테이블
       cursor.execute('''
       CREATE TABLE IF NOT EXISTS users (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           username TEXT NOT NULL UNIQUE,
           password_hash TEXT NOT NULL,
           role TEXT NOT NULL CHECK(role IN ('admin', 'operator', 'viewer')),
           created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
           last_login DATETIME,
           is_active BOOLEAN DEFAULT 1
       )
       ''')

       # Bunker 마스터 테이블
       cursor.execute('''
       CREATE TABLE IF NOT EXISTS bunkers (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           bunker_id TEXT NOT NULL UNIQUE,
           name TEXT NOT NULL,
           location TEXT,
           description TEXT,
           is_active BOOLEAN DEFAULT 1,
           created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
           updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
       )
       ''')

       # Stocker 마스터 테이블
       cursor.execute('''
       CREATE TABLE IF NOT EXISTS stockers (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           stocker_id TEXT NOT NULL UNIQUE,
           bunker_id TEXT,
           name TEXT NOT NULL,
           ip_address TEXT,
           port TEXT CHECK(port IN ('A', 'B')),
           description TEXT,
           is_active BOOLEAN DEFAULT 1,
           created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
           updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
           FOREIGN KEY (bunker_id) REFERENCES bunkers(bunker_id)
       )
       ''')

       # Gas Cabinet 마스터 테이블
       cursor.execute('''
       CREATE TABLE IF NOT EXISTS gas_cabinets (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           cabinet_id TEXT NOT NULL UNIQUE,
           bunker_id TEXT,
           name TEXT NOT NULL,
           ip_address TEXT,
           port TEXT CHECK(port IN ('A', 'B')),
           gas_type TEXT,
           description TEXT,
           is_active BOOLEAN DEFAULT 1,
           created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
           updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
           FOREIGN KEY (bunker_id) REFERENCES bunkers(bunker_id)
       )
       ''')

       # AGV 마스터 테이블
       cursor.execute('''
       CREATE TABLE IF NOT EXISTS agvs (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           agv_id TEXT NOT NULL UNIQUE,
           name TEXT NOT NULL,
           ip_address TEXT,
           agv_type TEXT,
           description TEXT,
           is_active BOOLEAN DEFAULT 1,
           created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
           updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
       )
       ''')

       # 트리거 생성
       cursor.execute('''
       CREATE TRIGGER IF NOT EXISTS update_bunkers_timestamp 
       AFTER UPDATE ON bunkers
       BEGIN
           UPDATE bunkers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
       END
       ''')

       cursor.execute('''
       CREATE TRIGGER IF NOT EXISTS update_stockers_timestamp 
       AFTER UPDATE ON stockers
       BEGIN
           UPDATE stockers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
       END
       ''')

       cursor.execute('''
       CREATE TRIGGER IF NOT EXISTS update_gas_cabinets_timestamp 
       AFTER UPDATE ON gas_cabinets
       BEGIN
           UPDATE gas_cabinets SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
       END
       ''')

       cursor.execute('''
       CREATE TRIGGER IF NOT EXISTS update_agvs_timestamp 
       AFTER UPDATE ON agvs
       BEGIN
           UPDATE agvs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
       END
       ''')

       conn.commit()
       logger.info("운영 DB 테이블 생성 완료")

   except Exception as e:
       logger.error(f"운영 DB 초기화 중 오류 발생: {e}")
       if conn:
           conn.rollback()
   finally:
       if conn:
           conn.close()
           
def init_stocker_history_db():
    """Stocker 히스토리 데이터베이스 초기화"""
    db_dir = Path("src/data/db/history")
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "stocker_history.db"

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Stocker 이력 테이블
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocker_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stocker_id TEXT NOT NULL,
            port TEXT CHECK(port IN ('A', 'B')),
            status_data JSON NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Stocker 알람 이력 테이블
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocker_alarm_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stocker_id TEXT NOT NULL,
            port TEXT CHECK(port IN ('A', 'B')),
            alarm_code INTEGER NOT NULL,
            alarm_description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            cleared_at DATETIME
        )
        ''')

        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stocker_history_id ON stocker_history(stocker_id, port)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stocker_alarm_id ON stocker_alarm_history(stocker_id, port)')

        conn.commit()
        logger.info("Stocker 히스토리 DB 테이블 생성 완료")

    except Exception as e:
        logger.error(f"Stocker 히스토리 DB 초기화 중 오류 발생: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def init_gas_cabinet_history_db():
    """Gas Cabinet 히스토리 데이터베이스 초기화"""
    db_dir = Path("src/data/db/history")
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "gas_cabinet_history.db"

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Gas Cabinet 이력 테이블
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gas_cabinet_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cabinet_id TEXT NOT NULL,
            port TEXT CHECK(port IN ('A', 'B')),
            status_data JSON NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Gas Cabinet 알람 이력 테이블
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gas_cabinet_alarm_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cabinet_id TEXT NOT NULL,
            port TEXT CHECK(port IN ('A', 'B')),
            alarm_code INTEGER NOT NULL,
            alarm_description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            cleared_at DATETIME
        )
        ''')

        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cabinet_history_id ON gas_cabinet_history(cabinet_id, port)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cabinet_alarm_id ON gas_cabinet_alarm_history(cabinet_id, port)')

        conn.commit()
        logger.info("Gas Cabinet 히스토리 DB 테이블 생성 완료")

    except Exception as e:
        logger.error(f"Gas Cabinet 히스토리 DB 초기화 중 오류 발생: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def init_agv_history_db():
    """AGV 히스토리 데이터베이스 초기화"""
    db_dir = Path("src/data/db/history")
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "agv_history.db"

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # AGV 이력 테이블
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS agv_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agv_id TEXT NOT NULL,
            status_data JSON NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # AGV 알람 이력 테이블
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS agv_alarm_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agv_id TEXT NOT NULL,
            alarm_code INTEGER NOT NULL,
            alarm_description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            cleared_at DATETIME
        )
        ''')

        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agv_history_id ON agv_history(agv_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_agv_alarm_id ON agv_alarm_history(agv_id)')

        conn.commit()
        logger.info("AGV 히스토리 DB 테이블 생성 완료")

    except Exception as e:
        logger.error(f"AGV 히스토리 DB 초기화 중 오류 발생: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info("데이터베이스 초기화 시작")
    init_operational_db()
    init_stocker_history_db()
    init_gas_cabinet_history_db()
    init_agv_history_db()
    logger.info("데이터베이스 초기화 완료")

