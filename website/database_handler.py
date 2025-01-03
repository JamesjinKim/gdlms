import sqlite3
import json
import logging
import os
from datetime import datetime

class DatabaseHandler:
    def __init__(self, db_path):
        """
        DatabaseHandler 초기화
        Args:
            db_path (str): SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """데이터베이스 및 테이블 초기화"""
        try:
            # 데이터베이스 디렉토리 확인 및 생성
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            # 데이터베이스 연결 및 테이블 생성
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 테이블 생성
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS modbus_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        message_type TEXT NOT NULL,
                        function_code INTEGER NOT NULL,
                        register_address INTEGER NOT NULL,
                        register_data TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logging.info(f"Database initialized at: {self.db_path}")

        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
            raise

    def save_message(self, message_data):
        """
        Modbus 메시지 저장
        Args:
            message_data (dict): 저장할 메시지 데이터
        Returns:
            int: 저장된 레코드의 ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO modbus_messages (
                        timestamp,
                        message_type,
                        function_code,
                        register_address,
                        register_data
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    message_data['timestamp'],
                    message_data['type'],
                    message_data['function_code'],
                    message_data['address'],
                    json.dumps(message_data['values'])
                ))
                
                conn.commit()
                last_id = cursor.lastrowid
                logging.info(f"Saved message with ID: {last_id}")
                return last_id

        except sqlite3.Error as e:
            logging.error(f"Error saving message: {e}")
            raise

    def get_recent_messages(self, limit=100):
        """
        최근 메시지 조회
        Args:
            limit (int): 조회할 최대 메시지 수
        Returns:
            list: 메시지 목록
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM modbus_messages 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                messages = []
                for row in rows:
                    message = dict(row)
                    message['values'] = json.loads(message['register_data'])
                    messages.append(message)
                
                return messages

        except sqlite3.Error as e:
            logging.error(f"Error retrieving messages: {e}")
            return []

    def get_message_count(self):
        """
        전체 메시지 수 조회
        Returns:
            int: 전체 메시지 수
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM modbus_messages")
                return cursor.fetchone()[0]

        except sqlite3.Error as e:
            logging.error(f"Error getting message count: {e}")
            return 0

    def clear_old_messages(self, days=30):
        """
        오래된 메시지 삭제
        Args:
            days (int): 보관할 날짜 수
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM modbus_messages 
                    WHERE created_at < datetime('now', '-? days')
                """, (days,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                logging.info(f"Cleared {deleted_count} old messages")
                return deleted_count

        except sqlite3.Error as e:
            logging.error(f"Error clearing old messages: {e}")
            raise