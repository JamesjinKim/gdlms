# src/backend/common/db_base.py

import sqlite3
from contextlib import contextmanager
import json
from datetime import datetime

class BaseDBHandler:
   """데이터베이스 핸들링을 위한 기본 클래스
   모든 DB 핸들러는 이 클래스를 상속받아 구현"""
   
   def __init__(self, db_path):
       # SQLite DB 파일 경로를 저장
       self.db_path = db_path

   @contextmanager
   def get_connection(self):
       """DB 연결을 관리하는 컨텍스트 매니저
       # 사용 예시:
       # with self.get_connection() as conn:
       #     cursor = conn.cursor()
       #     cursor.execute("SELECT * FROM table")
       """
       # SQLite DB 연결 생성
       conn = sqlite3.connect(self.db_path)
       
       # 조회 결과를 딕셔너리 형태로 받기 위한 설정
       # 예: row['column_name'] 형태로 접근 가능
       conn.row_factory = sqlite3.Row
       
       try:
           # connection 객체를 yield하여 컨텍스트 내에서 사용할 수 있게 함
           yield conn
       finally:
           # 컨텍스트를 벗어날 때 자동으로 연결 종료
           # 에러가 발생하더라도 반드시 연결이 종료됨
           conn.close()

class OperationalDBHandler(BaseDBHandler):
   """실시간 운영 데이터를 다루는 DB 핸들러"""
   
   def update_equipment_status(self, equipment_type, equipment_id, status_data):
       """장비 상태 정보를 업데이트하거나 새로 추가
       
       # 매개변수:
       # equipment_type: 장비 종류 (stocker, gas_cabinet, agv)
       # equipment_id: 장비 고유 ID
       # status_data: 장비 상태 정보를 담은 딕셔너리
       """
       with self.get_connection() as conn:
           cursor = conn.cursor()
           cursor.execute("""
               INSERT OR REPLACE INTO current_equipment_status 
               (equipment_type, equipment_id, status_data, last_updated)
               VALUES (?, ?, ?, ?)
           """, (equipment_type, equipment_id, json.dumps(status_data), datetime.now()))
           conn.commit()

   def get_current_status(self, equipment_type=None):
       """현재 장비 상태 정보를 조회
       
       # 매개변수:
       # equipment_type: 장비 종류 (선택적). None이면 모든 장비 조회
       
       # 반환값:
       # 장비 상태 정보 리스트. 각 항목은 딕셔너리 형태
       """
       with self.get_connection() as conn:
           cursor = conn.cursor()
           if equipment_type:
               cursor.execute("""
                   SELECT * FROM current_equipment_status 
                   WHERE equipment_type = ?
               """, (equipment_type,))
           else:
               cursor.execute("SELECT * FROM current_equipment_status")
           # SQLite 조회 결과를 딕셔너리 리스트로 변환하여 반환
           return [dict(row) for row in cursor.fetchall()]

class HistoryDBHandler(BaseDBHandler):
   """히스토리 데이터를 다루는 DB 핸들러"""
   
   def add_history_record(self, equipment_type, equipment_id, status_data):
       """히스토리 레코드 추가
       
       # 매개변수:
       # equipment_type: 장비 종류 (stocker, gas_cabinet, agv)
       # equipment_id: 장비 고유 ID
       # status_data: 장비 상태 정보를 담은 딕셔너리
       """
       with self.get_connection() as conn:
           cursor = conn.cursor()
           cursor.execute("""
               INSERT INTO equipment_history 
               (equipment_type, equipment_id, status_data)
               VALUES (?, ?, ?)
           """, (equipment_type, equipment_id, json.dumps(status_data)))
           conn.commit()

   def get_history(self, equipment_type, start_time, end_time):
       """특정 기간 동안의 히스토리 데이터 조회
       
       # 매개변수:
       # equipment_type: 장비 종류
       # start_time: 조회 시작 시간
       # end_time: 조회 종료 시간
       
       # 반환값:
       # 히스토리 레코드 리스트. 각 항목은 딕셔너리 형태
       """
       with self.get_connection() as conn:
           cursor = conn.cursor()
           cursor.execute("""
               SELECT * FROM equipment_history
               WHERE equipment_type = ? 
               AND timestamp BETWEEN ? AND ?
               ORDER BY timestamp DESC
           """, (equipment_type, start_time, end_time))
           return [dict(row) for row in cursor.fetchall()]

# DBManager 클래스는 운영 DB와 히스토리 DB를 통합 관리
class DBManager:
   """DB 통합 관리 클래스"""
   
   def __init__(self):
       # 운영 DB와 히스토리 DB 핸들러 초기화
       self.operational_db = OperationalDBHandler('src/data/db/operational/operational.db')
       self.history_db = HistoryDBHandler('src/data/db/history/history.db')

   async def update_equipment_data(self, equipment_type, equipment_id, data):
       """장비 데이터 통합 업데이트
       운영 DB와 히스토리 DB에 모두 데이터를 기록
       
       # 매개변수:
       # equipment_type: 장비 종류
       # equipment_id: 장비 고유 ID
       # data: 장비 상태 데이터
       """
       # 운영 DB 업데이트
       self.operational_db.update_equipment_status(equipment_type, equipment_id, data)
       # 히스토리 DB에 기록
       self.history_db.add_history_record(equipment_type, equipment_id, data)