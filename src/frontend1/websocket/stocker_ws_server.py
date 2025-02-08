# src/frontend/websocket/stocker_ws_server.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
import asyncio
import json
from datetime import datetime
import logging
from pathlib import Path

# 로깅 설정
log_dir = Path("src/data/logs/websocket")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "stocker_websocket.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockerConnectionManager:
    """Stocker WebSocket 연결 관리 클래스"""
    
    def __init__(self):
        # 활성화된 웹소켓 연결들을 저장
        self.active_connections: List[WebSocket] = []
        # 마지막으로 수신한 Stocker 데이터
        self.last_data: Dict = {}

    async def connect(self, websocket: WebSocket):
        """새로운 WebSocket 연결 수립"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New client connected. Total connections: {len(self.active_connections)}")
        
        # 연결 즉시 마지막 데이터 전송
        if self.last_data:
            await self.send_personal_message(self.last_data, websocket)

    def disconnect(self, websocket: WebSocket):
        """WebSocket 연결 종료"""
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Remaining connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: Dict, websocket: WebSocket):
        """특정 클라이언트에게 메시지 전송"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")

    async def broadcast(self, message: Dict):
        """모든 연결된 클라이언트에게 메시지 브로드캐스트"""
        # 마지막 데이터 업데이트
        self.last_data = message
        
        # 연결된 모든 클라이언트에게 전송
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")
                # 문제가 있는 연결 제거
                await self.disconnect(connection)

app = FastAPI()
manager = StockerConnectionManager()

@app.websocket("/ws/stocker")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 엔드포인트"""
    await manager.connect(websocket)
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                # 타임스탬프 추가
                message['timestamp'] = datetime.now().isoformat()
                
                # 모든 연결된 클라이언트에게 브로드캐스트
                await manager.broadcast(message)
                logger.debug(f"Broadcasted message: {message}")
                
            except json.JSONDecodeError:
                logger.error("Invalid JSON format received")
                await websocket.send_text("Error: Invalid JSON format")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행되는 이벤트"""
    logger.info("Stocker WebSocket Server started")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 실행되는 이벤트"""
    logger.info("Stocker WebSocket Server shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)