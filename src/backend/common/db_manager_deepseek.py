# src/backend/common/db_manager.py
#import aiosqlite  # 변경: sqlite3 → aiosqlite
import sqlite3 # 이부분은 선택적 사항으로 주의 필요.
from pathlib import Path
import json
import logging
from typing import Dict, Any

class DBManager:
    def __init__(self):
        self.db_dir = Path("src/data/db/history")
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.history_db_path = self.db_dir / "stocker_history.db"
        # 로깅 설정
        self.logger = logging.getLogger(__name__)
        
        # DB 및 테이블 초기화
        self.init_db()

    async def init_db(self):  # 비동기로 변경
        """DB 테이블 초기화 (비동기)"""
        async with sqlite3.connect(str(self.history_db_path)) as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS stocker_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stocker_id TEXT NOT NULL,
                    status_data TEXT NOT NULL,  # SQLite는 JSON 타입 대신 TEXT 사용
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Stocker 알람 이력 테이블
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS stocker_alarm_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stocker_id TEXT NOT NULL,
                    alarm_code INTEGER NOT NULL,
                    alarm_description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cleared_at DATETIME
                )
            ''')
            await conn.commit()
            self.logger.info("DB 테이블 초기화 완료")

    async def update_data(self, stocker_id: str, data: Dict[str, Any]):
        """Stocker 데이터 히스토리 DB에 저장 (비동기)"""
        try:
            async with sqlite3.connect(str(self.history_db_path)) as conn:
                await conn.execute(
                    "INSERT INTO stocker_history (stocker_id, status_data) VALUES (?, ?)",
                    (stocker_id, json.dumps(data))  # JSON 직렬화
                )
                await conn.commit()
                self.logger.info(f"DB Manager - Data saved: {stocker_id}")
        except Exception as e:
            self.logger.error(f"DB Manager - DB 저장 실패: {e}", exc_info=True)
            raise

    async def save_alarm(self, stocker_id: str, alarm_code: int, description: str):
        """알람 데이터 저장 (비동기)"""
        try:
            async with sqlite3.connect(str(self.history_db_path)) as conn:
                await conn.execute(
                    """INSERT INTO stocker_alarm_history 
                    (stocker_id, alarm_code, alarm_description)
                    VALUES (?, ?, ?)""",
                    (stocker_id, alarm_code, description)
                )
                await conn.commit()
                self.logger.info(f"Alarm saved: {stocker_id}")
        except Exception as e:
            self.logger.error(f"알람 저장 실패: {e}", exc_info=True)
            raise