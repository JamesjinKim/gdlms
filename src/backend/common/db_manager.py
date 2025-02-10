import asyncio
import logging
import os
import sys
from pathlib import Path
import sqlite3
import time
from typing import Dict, Any
import json
import aiosqlite
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 핸들러 중복 방지
if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

class DBManager:
    def __init__(self, history_type: str):
        self._lock = asyncio.Lock()
        self.SAVE_INTERVAL = 1.0  # 1초 간격
        self.BATCH_SIZE = 10  # 최대 배치 크기
        
        # 기존 초기화 코드 유지
        project_root = Path(__file__).parent.parent
        db_dir = project_root / "data" / "history"
        os.makedirs(db_dir, exist_ok=True)
        
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

        # 데이터 큐 초기화
        self._data_queue = []
        self._alarm_queue = []

        # 데이터베이스 테이블 생성
        self._create_tables()

        # 주기적 배치 저장 태스크 시작
        self._batch_save_task = None

    def _create_tables(self):
        """데이터베이스 테이블 생성"""
        try:
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

                # 인덱스 추가
                # 히스토리 테이블 인덱스
                cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS idx_{self.history_table}_created_at 
                ON {self.history_table} (created_at)
                ''')

                # 디바이스 ID 인덱스
                cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS idx_{self.history_table}_device_id 
                ON {self.history_table} ({self.history_table.split('_')[0]}_id)
                ''')

                # 알람 테이블 인덱스
                cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS idx_{self.alarm_table}_created_at 
                ON {self.alarm_table} (created_at)
                ''')

                cursor.execute(f'''
                CREATE INDEX IF NOT EXISTS idx_{self.alarm_table}_device_id 
                ON {self.alarm_table} ({self.alarm_table.split('_')[0]}_id)
                ''')

                conn.commit()
                logging.info(f"Database Tables Initialized: {self.history_table}, {self.alarm_table}")
        except Exception as e:
            logging.error(f"Table Creation Error: {e}")
            raise

    def start_batch_save(self):
        """배치 저장 프로세스 시작"""
        if self._batch_save_task is None:
            self._batch_save_task = asyncio.create_task(self._periodic_batch_save())

    def stop_batch_save(self):
        """배치 저장 프로세스 중지"""
        if self._batch_save_task:
            self._batch_save_task.cancel()
            self._batch_save_task = None

    async def _periodic_batch_save(self):
        """주기적으로 배치 저장 수행"""
        while True:
            try:
                await asyncio.sleep(self.SAVE_INTERVAL)
                
                # 데이터 배치 저장
                if self._data_queue:
                    await self._save_data_batch()
                
                # 알람 배치 저장
                if self._alarm_queue:
                    await self._save_alarm_batch()
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Batch save error: {e}")

    async def _save_data_batch(self):
        """데이터 배치 저장"""
        if not self._data_queue:
            return

        try:
            db_path = str(self.history_db_path.resolve())
            async with aiosqlite.connect(db_path) as conn:
                # 트랜잭션 시작
                await conn.execute('BEGIN')
                
                for item in self._data_queue[:self.BATCH_SIZE]:
                    await conn.execute(
                        f"INSERT INTO {self.history_table} "
                        f"({item['device_id'].split('_')[0]}_id, status_data, created_at) "
                        f"VALUES (?, ?, ?)",
                        (item['device_id'], 
                         json.dumps(item['data']), 
                         item['timestamp'].strftime("%Y-%m-%d %H:%M:%S"))
                    )
                
                # 트랜잭션 커밋
                await conn.commit()
                
                # 처리된 데이터 큐에서 제거
                del self._data_queue[:self.BATCH_SIZE]
                
                logging.info(f"Data batch saved: {self.BATCH_SIZE} records")

        except Exception as e:
            logging.error(f"Data batch save error: {e}")
            # 오류 시 롤백
            await conn.rollback()
    
    # batch job과 즉시성 을 구분하여 하이브리드로 작성 예정
    async def _save_alarm_batch(self):
        """알람 배치 저장"""
        if not self._alarm_queue:
            return

        try:
            db_path = str(self.history_db_path.resolve())
            async with aiosqlite.connect(db_path) as conn:
                await conn.execute('BEGIN')
                
                for item in self._alarm_queue[:self.BATCH_SIZE]:
                    await conn.execute(
                        f"INSERT INTO {self.alarm_table} "
                        f"({self.alarm_table.split('_')[0]}_id, alarm_code, alarm_description, created_at) "
                        f"VALUES (?, ?, ?, ?)",
                        (item['device_id'], 
                        item['alarm_code'], 
                        item['description'], 
                        item['timestamp'].strftime("%Y-%m-%d %H:%M:%S"))
                    )
                
                await conn.commit()
                
                # 처리된 알람 큐에서 제거
                del self._alarm_queue[:self.BATCH_SIZE]
                
                logger.info(f"Alarm batch saved: {self.BATCH_SIZE} records")

        except Exception as e:
            logger.error(f"Alarm batch save error: {e}")
            # 추가적인 오류 정보 로깅
            logger.error(f"Alarm queue contents: {self._alarm_queue}")

    async def update_data(self, device_id: str, data: Dict[str, Any]):
        """데이터를 큐에 추가"""
        # 중복 데이터 방지 로직 (옵션)
        if self._data_queue and self._data_queue[-1]['device_id'] == device_id:
            last_data = json.dumps(self._data_queue[-1]['data'], sort_keys=True)
            current_data = json.dumps(data, sort_keys=True)
            
            if last_data == current_data:
                return

        self._data_queue.append({
            'device_id': device_id, 
            'data': data, 
            'timestamp': datetime.now(timezone.utc).astimezone(ZoneInfo("Asia/Seoul"))
        })

        # 배치 크기 도달 시 즉시 저장
        if len(self._data_queue) >= self.BATCH_SIZE:
            await self._save_data_batch()

    async def save_alarm(self, device_id: str, alarm_code: int, description: str):
        """알람을 큐에 추가"""
        # 중복 알람 방지 로직 (옵션)
        if self._alarm_queue and self._alarm_queue[-1]['device_id'] == device_id:
            last_alarm = self._alarm_queue[-1]
            if (last_alarm['alarm_code'] == alarm_code and 
                last_alarm['description'] == description):
                return

        self._alarm_queue.append({
            'device_id': device_id,
            'alarm_code': alarm_code,
            'description': description,
            'timestamp': datetime.now(timezone.utc).astimezone(ZoneInfo("Asia/Seoul"))
        })

        # 배치 크기 도달 시 즉시 저장
        if len(self._alarm_queue) >= self.BATCH_SIZE:
            await self._save_alarm_batch()