import json
import aiosqlite


# src/backend/common/db_handler.py
class EquipmentDBHandler:
    def __init__(self, db_path):
        self.db_path = db_path

    async def save_status(self, equipment_type, equipment_id, status_data):
        """상태 데이터 저장"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO equipment_status (
                    equipment_type, equipment_id, status_data
                ) VALUES (?, ?, ?)
            """, (equipment_type, equipment_id, json.dumps(status_data)))
            await db.commit()

    async def get_history(self, equipment_type, start_time, end_time):
        """히스토리 데이터 조회"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT * FROM equipment_status
                WHERE equipment_type = ? 
                AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            """, (equipment_type, start_time, end_time))
            return await cursor.fetchall()