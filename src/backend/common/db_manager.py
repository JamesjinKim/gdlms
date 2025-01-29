# src/backend/common/db_manager.py
import json
import logging
import aiosqlite
import sqlite3
from typing import Dict, Any
from pathlib import Path
import os

class DBManager:
    def __init__(self, history_type: str):
        """
        DBManager 초기화
        
        :param history_type: 히스토리 타입 ('stocker', 'gas_cabinet', 'agv')
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 프로젝트 루트 디렉토리 (src) 기준으로 데이터베이스 경로 설정
        project_root = Path(__file__).parent.parent
        db_dir = project_root / "data" / "db"
        
        # 디렉토리 생성 (존재하지 않으면)
        os.makedirs(db_dir, exist_ok=True)
        
        # 히스토리 타입에 따른 데이터베이스 경로 결정
        if history_type == 'stocker':
            self.history_db_path = db_dir / "stocker_history.db"
            self.history_table = "stocker_history"
            self.alarm_table = "stocker_alarm_history"
        elif history_type == 'gas_cabinet':
            self.history_db_path = db_dir / "gas_cabinet_history.db"
            self.history_table = "gas_cabinet_history"
            self.alarm_table = "gas_cabinet_alarm_history"
        elif history_type == 'agv':
            self.history_db_path = db_dir / "agv_history.db"
            self.history_table = "agv_history"
            self.alarm_table = "agv_alarm_history"
        else:
            raise ValueError(f"Invalid history type: {history_type}")
        
        # 데이터베이스 테이블 생성
        self._create_tables()

    def _create_tables(self):
        """데이터베이스 테이블 생성"""
        try:
            # 절대 경로로 변환하고 문자열로 변환
            db_path = str(self.history_db_path.resolve())
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # 히스토리 테이블 생성
                cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.history_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {self.history_table.split('_')[0]}_id TEXT NOT NULL,
                    status_data JSON NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                ''')

                # 알람 테이블 생성
                cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.alarm_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {self.alarm_table.split('_')[0]}_id TEXT NOT NULL,
                    alarm_code INTEGER NOT NULL,
                    alarm_description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    cleared_at DATETIME
                )
                ''')

                conn.commit()
                self.logger.info(f"{self.history_table} 및 {self.alarm_table} 테이블 생성 완료")
        except Exception as e:
            self.logger.error(f"테이블 생성 중 오류 발생: {e}")
            raise

    async def update_data(self, device_id: str, data: Dict[str, Any]):
        """장치 데이터를 히스토리 DB에 저장"""
        try:
            # 절대 경로로 변환하고 문자열로 변환
            db_path = str(self.history_db_path.resolve())
            
            async with aiosqlite.connect(db_path) as conn:
                # JSON으로 직렬화
                status_data = json.dumps(data)
                
                await conn.execute(f"""
                    INSERT INTO {self.history_table} 
                    ({device_id.split('_')[0]}_id, status_data) 
                    VALUES (?, ?)
                """, (device_id, status_data))
                
                await conn.commit()
                self.logger.info(f"Data saved for {device_id}")
                
        except Exception as e:
            self.logger.error(f"DB 저장 오류: {e}")
            raise  # 호출자에게 오류 전파

    async def save_alarm(self, device_id: str, alarm_code: int, description: str):
        """알람 데이터 저장"""
        try:
            # 절대 경로로 변환하고 문자열로 변환
            db_path = str(self.history_db_path.resolve())
            
            async with aiosqlite.connect(db_path) as conn:
                await conn.execute(f"""
                    INSERT INTO {self.alarm_table} 
                    ({device_id.split('_')[0]}_id, alarm_code, alarm_description) 
                    VALUES (?, ?, ?)
                """, (device_id, alarm_code, description))
                
                await conn.commit()
                self.logger.info(f"Alarm saved for {device_id}")
                
        except Exception as e:
            self.logger.error(f"알람 저장 오류: {e}")
            raise  # 호출자에게 오류 전파