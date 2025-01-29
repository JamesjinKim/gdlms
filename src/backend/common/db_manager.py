# src/backend/common/db_manager.py
class DBManager:
    def __init__(self):
        self._current_data = {
            'gas_cabinet': {},
            'stocker': {},
            'agv': {}
        }
        self._subscribers = []

    async def update_data(self, device_type, data):
        # 현재 데이터 업데이트
        self._current_data[device_type] = data
        # WebSocket 구독자들에게 알림
        await self._notify_subscribers(device_type, data)