# src/backend/common/db_manager.py
import asyncio
import logging
import os
import sys
from pathlib import Path
import sqlite3
from typing import Dict, Any
import json
import aiosqlite
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# UTC 현재 시간을 Seoul 시간으로 변환
seoul_time = datetime.now(timezone.utc).astimezone(ZoneInfo("Asia/Seoul"))
# 원하는 포맷으로 문자열 변환
seoul_time_str = seoul_time.strftime("%Y-%m-%d %H:%M:%S")

# 로거 설정을 모듈 수준에서 한 번만 수행
def setup_logger():
    logger = logging.getLogger(__name__)
    
    # 기존 핸들러 제거
    logger.handlers.clear()
    
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # 핸들러 중복 방지
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# 모듈 로드 시 한 번만 로거 설정
logger = setup_logger()

class DBManager:
    def __init__(self, history_type: str):
        # 프로젝트 루트 디렉토리 (src) 기준으로 데이터베이스 경로 설정
        project_root = Path(__file__).parent.parent
        db_dir = project_root / "data" / "history"
        
        # 디렉토리 생성 (존재하지 않으면)
        os.makedirs(db_dir, exist_ok=True)
        
        # 히스토리 타입에 따른 데이터베이스 경로 결정
        history_config = {
            'stocker': {
                'db_path': db_dir / "stocker_history.db",
                'history_table': "stocker_history",
                'alarm_table': "stocker_alarm_history"
            },
            'gas_cabinet': {
                'db_path': db_dir / "gas_cabinet_history.db",
                'history_table': "gas_cabinet_history",
                'alarm_table': "gas_cabinet_alarm_history"
            },
            'agv': {
                'db_path': db_dir / "agv_history.db",
                'history_table': "agv_history",
                'alarm_table': "agv_alarm_history"
            }
        }
        
        # 타입 검증 및 설정
        if history_type not in history_config:
            raise ValueError(f"Invalid history type: {history_type}")
        
        config = history_config[history_type]
        self.history_db_path = config['db_path']
        self.history_table = config['history_table']
        self.alarm_table = config['alarm_table']

        # 데이터베이스 테이블 생성 (한 번만 수행)
        self._create_tables()

        # last_alarm 딕셔너리 초기화
        self.last_alarm = {}  # 마지막으로 저장된 알람 추적
        self._alarm_lock = asyncio.Lock()  # 동시성 제어를 위한 Lock 추가

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
                    created_at DATETIME DEFAULT (datetime('now', 'localtime'))
                )
                ''')

                # 알람 테이블 생성
                cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.alarm_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {self.alarm_table.split('_')[0]}_id TEXT NOT NULL,
                    alarm_code INTEGER NOT NULL,
                    alarm_description TEXT,
                    created_at DATETIME DEFAULT (datetime('now', 'localtime'))
                )
                ''')

                conn.commit()
                logger.info(f"Database Tables Initialized: {self.history_table}, {self.alarm_table}")
        except Exception as e:
            logger.error(f"Table Creation Error: {e}")
            raise

    async def update_data(self, device_id: str, data: Dict[str, Any]):
        """장치 데이터를 히스토리 DB에 저장"""
        try:
            # 절대 경로로 변환하고 문자열로 변환
            db_path = str(self.history_db_path.resolve())
            
            async with aiosqlite.connect(db_path) as conn:
                # JSON으로 직렬화
                status_data = json.dumps(data)
                
                # UTC 시간을 Seoul 시간으로 변환
                current_time = datetime.now(timezone.utc).astimezone(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")

                await conn.execute(f"""
                    INSERT INTO {self.history_table} 
                    ({device_id.split('_')[0]}_id, status_data, created_at) 
                    VALUES (?, ?, ?)
                """, (device_id, status_data, current_time))
                
                await conn.commit()
                logger.info(f"Data saved for device: {device_id}, table: {self.history_table}")

                # 알람 코드 확인 및 저장
                alarm_code = data.get('plc_data', {}).get('alarm_code', 0)
                logger.info(f"Alarm saved for device: {device_id}, code: {alarm_code}")

        except Exception as e:
            logger.error(f"DB 저장 오류: {e}")
            raise

    async def save_alarm(self, device_id: str, alarm_code: int, description: str):
        """알람 데이터 저장 (중복 방지)"""
        async with self._alarm_lock:  # 동시성 제어
            try:
                # 동일한 알람 중복 체크
                if (device_id not in self.last_alarm or 
                    self.last_alarm[device_id] != alarm_code):
                    
                    db_path = str(self.history_db_path.resolve())
                    
                    # UTC 시간을 Seoul 시간으로 변환
                    current_time = datetime.now(timezone.utc).astimezone(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
                    
                    async with aiosqlite.connect(db_path) as conn:
                        await conn.execute(f"""
                            INSERT INTO {self.alarm_table} 
                            ({device_id.split('_')[0]}_id, alarm_code, alarm_description, created_at) 
                            VALUES (?, ?, ?, ?)
                        """, (device_id, alarm_code, description, current_time))
                        
                        await conn.commit()
                        logger.info(f"Alarm saved for device: {device_id}, code: {alarm_code}")
                    
                    # 마지막 알람 업데이트
                    self.last_alarm[device_id] = alarm_code
                else:
                    logger.debug(f"Duplicate alarm skipped for device: {device_id}, code: {alarm_code}")
                
            except Exception as e:
                logger.error(f"Alarm 저장 오류 (device: {device_id}, code: {alarm_code}): {e}")
                raise