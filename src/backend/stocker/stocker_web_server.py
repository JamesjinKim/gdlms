from datetime import datetime
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
import os
import json
from typing import List, Dict, Optional
from contextlib import asynccontextmanager
from pymodbus.client import AsyncModbusTcpClient
from stocker_alarm_codes import stocker_alarm_code
import uvicorn
import sys
from contextlib import asynccontextmanager

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger("StockerWebServer")

class ModbusDataClient:
    def __init__(self):
        self.client = None
        self.connected = False
        self.unit = 1
        self.last_data = None
        self.running = True
        self._lock = asyncio.Lock()
        self.update_interval = 1.0  # 데이터 업데이트 간격 (초)
        self.last_update = 0

    async def connect(self):
        """Modbus 클라이언트 연결"""
        try:
            async with self._lock:
                if self.client is None or not self.client.connected:
                    self.client = AsyncModbusTcpClient('127.0.0.1', port=5021)
                    self.connected = await self.client.connect()
                    if self.connected:
                        logger.info("Modbus 서버에 연결됨")
                    else:
                        logger.error("Modbus 서버 연결 실패")
                        await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"연결 오류: {e}")
            self.connected = False
            await asyncio.sleep(5)

    async def get_data(self) -> Optional[Dict]:
        try:
            if not self.connected:
                await self.connect()
                if not self.connected:
                    logger.error("Modbus 서버 연결 실패")
                    return None
            
            async with self._lock:
                # PLC 데이터 읽기
                results = []
                for start in range(0, 140, 50):
                    count = min(50, 140 - start)
                    result = await self.client.read_holding_registers(
                        address=start,
                        count=count,
                        slave=1
                    )
                    if result and not result.isError():
                        results.extend(result.registers)
                    else:
                        logger.error(f"레지스터 읽기 실패: {start}-{start+count}")
                        return None

                # bit_data도 holding register로 읽기
                bit_results = await self.client.read_holding_registers(
                    address=100,    # 시작 주소
                    count=18,       # 18개 word
                    slave=1
                )
                
                if not bit_results or bit_results.isError():
                    logger.error("비트 데이터 읽기 실패")
                    return None

                bit_values = bit_results.registers

                # 데이터 변환 로직
                current_data = {
                    "plc_data": {
                        "bunker_id": results[0] if len(results) > 0 else 0,
                        "stocker_id": results[1] if len(results) > 1 else 0,
                        "gas_type": results[2:7] if len(results) > 6 else [0]*5,
                        "status": {
                            "alarm_code": results[8] if len(results) > 8 else 0,
                            "alarm_message": stocker_alarm_code.get_description(results[8] if len(results) > 8 else 0)
                        },
                        "position": {
                            "x_axis": results[10] if len(results) > 10 else 0,
                            "z_axis": results[11] if len(results) > 11 else 0
                        },
                        "torque": {
                            "cap_open": results[12] if len(results) > 12 else 0,
                            "cap_close": results[13] if len(results) > 13 else 0
                        },
                        "port_a": {
                            "barcode": ''.join([chr(x) if 32 <= x <= 126 else '?' for x in results[30:60]]),
                            "gas_type": results[90:95] if len(results) > 94 else [0]*5
                        },
                        "port_b": {
                            "barcode": ''.join([chr(x) if 32 <= x <= 126 else '?' for x in results[60:90]]),
                            "gas_type": results[95:100] if len(results) > 99 else [0]*5
                        }
                    },
                    "bit_data": {
                        "word_100": {
                            "raw": bit_values[0],
                            "states": {
                                "EMG Signal": bool(bit_values[0] & (1 << 0)),
                                "Heart Bit": bool(bit_values[0] & (1 << 1)),
                                "Run/Stop Signal": bool(bit_values[0] & (1 << 2)),
                                "Server Connected Bit": bool(bit_values[0] & (1 << 3)),
                                "T-LAMP RED": bool(bit_values[0] & (1 << 4)),
                                "T-LAMP YELLOW": bool(bit_values[0] & (1 << 5)),
                                "T-LAMP GREEN": bool(bit_values[0] & (1 << 6)),
                                "Touch 수동동작中 Signal": bool(bit_values[0] & (1 << 7))
                            }
                        },
                        "word_105": {
                            "raw": bit_values[5],
                            "states": {
                                "port_a_cylinder": bool(bit_values[5] & (1 << 0)),
                                "port_b_cylinder": bool(bit_values[5] & (1 << 1)),
                                "port_a_worker_door_open": bool(bit_values[5] & (1 << 2)),
                                "port_a_worker_door_close": bool(bit_values[5] & (1 << 3)),
                                "port_a_bunker_door_open": bool(bit_values[5] & (1 << 4)),
                                "port_a_bunker_door_close": bool(bit_values[5] & (1 << 5)),
                                "port_b_worker_door_open": bool(bit_values[5] & (1 << 6)),
                                "port_b_worker_door_close": bool(bit_values[5] & (1 << 7)),
                                "port_b_bunker_door_open": bool(bit_values[5] & (1 << 8)),
                                "port_b_bunker_door_close": bool(bit_values[5] & (1 << 9))
                            }
                        },
                        "word_110": {
                            "raw": bit_values[10],
                            "states": {
                                "port_a_cap_open_complete": bool(bit_values[10] & (1 << 0)),
                                "port_a_cap_close_complete": bool(bit_values[10] & (1 << 1)),
                                "port_a_worker_door_open_complete": bool(bit_values[10] & (1 << 2)),
                                "port_a_worker_door_close_complete": bool(bit_values[10] & (1 << 3)),
                                "port_a_worker_input_ready": bool(bit_values[10] & (1 << 4)),
                                "port_a_worker_input_complete": bool(bit_values[10] & (1 << 5)),
                                "port_a_worker_output_ready": bool(bit_values[10] & (1 << 6)),
                                "port_a_worker_output_complete": bool(bit_values[10] & (1 << 7)),
                                "port_a_bunker_door_open_complete": bool(bit_values[10] & (1 << 8)),
                                "port_a_bunker_door_close_complete": bool(bit_values[10] & (1 << 9)),
                                "port_a_bunker_input_ready": bool(bit_values[10] & (1 << 10)),
                                "port_a_bunker_input_complete": bool(bit_values[10] & (1 << 11)),
                                "port_a_bunker_output_ready": bool(bit_values[10] & (1 << 12)),
                                "port_a_bunker_output_complete": bool(bit_values[10] & (1 << 13)),
                                "port_a_cylinder_align_in_progress": bool(bit_values[10] & (1 << 14)),
                                "port_a_cylinder_align_complete": bool(bit_values[10] & (1 << 15))
                            }
                        },
                        "word_111": {
                            "raw": bit_values[11],
                            "states": {
                                "port_a_cap_opening": bool(bit_values[11] & (1 << 0)),
                                "port_a_cap_closing": bool(bit_values[11] & (1 << 1)),
                                "port_a_x_axis_moving": bool(bit_values[11] & (1 << 2)),
                                "port_a_x_axis_complete": bool(bit_values[11] & (1 << 3)),
                                "port_a_finding_cap": bool(bit_values[11] & (1 << 4)),
                                "port_a_finding_cylinder_neck": bool(bit_values[11] & (1 << 5)),
                                "port_a_worker_door_opening": bool(bit_values[11] & (1 << 6)),
                                "port_a_worker_door_closing": bool(bit_values[11] & (1 << 7)),
                                "port_a_bunker_door_opening": bool(bit_values[11] & (1 << 8)),
                                "port_a_bunker_door_closing": bool(bit_values[11] & (1 << 9))
                            }
                        },
                        "word_115": {
                            "raw": bit_values[15],
                            "states": {
                                "port_b_cap_open_complete": bool(bit_values[15] & (1 << 0)),
                                "port_b_cap_close_complete": bool(bit_values[15] & (1 << 1)),
                                "port_b_worker_door_open_complete": bool(bit_values[15] & (1 << 2)),
                                "port_b_worker_door_close_complete": bool(bit_values[15] & (1 << 3)),
                                "port_b_worker_input_ready": bool(bit_values[15] & (1 << 4)),
                                "port_b_worker_input_complete": bool(bit_values[15] & (1 << 5)),
                                "port_b_worker_output_ready": bool(bit_values[15] & (1 << 6)),
                                "port_b_worker_output_complete": bool(bit_values[15] & (1 << 7)),
                                "port_b_bunker_door_open_complete": bool(bit_values[15] & (1 << 8)),
                                "port_b_bunker_door_close_complete": bool(bit_values[15] & (1 << 9)),
                                "port_b_bunker_input_ready": bool(bit_values[15] & (1 << 10)),
                                "port_b_bunker_input_complete": bool(bit_values[15] & (1 << 11)),
                                "port_b_bunker_output_ready": bool(bit_values[15] & (1 << 12)),
                                "port_b_bunker_output_complete": bool(bit_values[15] & (1 << 13)),
                                "port_b_cylinder_align_in_progress": bool(bit_values[15] & (1 << 14)),
                                "port_b_cylinder_align_complete": bool(bit_values[15] & (1 << 15))
                            }
                        },
                        "word_116": {
                            "raw": bit_values[16],
                            "states": {
                                "port_b_cap_opening": bool(bit_values[16] & (1 << 0)),
                                "port_b_cap_closing": bool(bit_values[16] & (1 << 1)),
                                "port_b_x_axis_moving": bool(bit_values[16] & (1 << 2)),
                                "port_b_x_axis_complete": bool(bit_values[16] & (1 << 3)),
                                "port_b_finding_cap": bool(bit_values[16] & (1 << 4)),
                                "port_b_finding_cylinder_neck": bool(bit_values[16] & (1 << 5)),
                                "port_b_worker_door_opening": bool(bit_values[16] & (1 << 6)),
                                "port_b_worker_door_closing": bool(bit_values[16] & (1 << 7)),
                                "port_b_bunker_door_opening": bool(bit_values[16] & (1 << 8)),
                                "port_b_bunker_door_closing": bool(bit_values[16] & (1 << 9))
                            }
                        }
                    }
                }

                return current_data

        except Exception as e:
            logger.error(f"데이터 읽기 중 예외 발생: {e}")
            self.connected = False
            return None
    
    async def close(self):
        try:
            self.running = False  # 실행 상태 플래그 해제
            if self.client and hasattr(self.client, 'connected') and self.client.connected:
                await self.client.close()
                print("Modbus 클라이언트가 정상적으로 종료되었습니다.")
            self.connected = False
        except Exception as e:
            print(f"Modbus 클라이언트 종료 중 오류: {e}")
        finally:
            self.client = None

    async def update_client_data(self):
        while self.running:  # running 플래그 확인
            try:
                current_time = time.time()
                if current_time - self.last_update >= self.update_interval:
                    data = await self.get_data()
                    if data:
                        await manager.broadcast(data)
                        self.last_update = current_time
                await asyncio.sleep(0.1)  # 짧은 대기 시간으로 CPU 부하 감소
            except Exception as e:
                logger.error(f"데이터 업데이트 오류: {e}")
                await asyncio.sleep(1)
    
class ConnectionManager:
    def __init__(self, batch_size: int = 10, max_connections: int = 50):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()
        self.max_connections = max_connections
        self.message_count = 0
        self.start_time = time.time()
        self.BATCH_SIZE = batch_size

    def reset_metrics(self):
        self.message_count = 0
        self.start_time = time.time()

    async def connect(self, websocket: WebSocket):
        async with self._lock:
            if len(self.active_connections) >= self.max_connections:
                await websocket.close(code=1008)
                logger.warning(f"최대 연결 수 초과로 연결 거부됨")
                return
                
            self.active_connections.append(websocket)
            logger.info(f"WebSocket 클라이언트 연결됨. 현재 연결 수: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket 클라이언트 연결 해제. 현재 연결 수: {len(self.active_connections)}")

    async def broadcast(self, data: dict):
        if not self.active_connections:
            return

        self.message_count += 1
        if self.message_count % 1000 == 0:
            elapsed = time.time() - self.start_time
            msg_per_sec = self.message_count / elapsed
            logger.info(f"메시지 처리율: {msg_per_sec:.2f} messages/sec")
            if self.message_count >= 1000000:  # 백만 건마다 메트릭 리셋
                self.reset_metrics()

        for i in range(0, len(self.active_connections), self.BATCH_SIZE):
            batch = self.active_connections[i:i + self.BATCH_SIZE]
            try:
                await asyncio.gather(
                    *[self._send_to_client(client, data) for client in batch],
                    return_exceptions=True
                )
            except Exception as e:
                logger.error(f"배치 전송 중 오류: {e}")
    
    async def _send_to_client(self, websocket: WebSocket, data: dict):
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"클라이언트 전송 오류: {e}")
            await self.disconnect(websocket)

manager = ConnectionManager()

# ModbusDataClient 인스턴스를 전역 변수로 설정
modbus_client: Optional[ModbusDataClient] = None

async def startup():
    """애플리케이션 시작 시 실행될 코드"""
    global modbus_client
    try:
        modbus_client = ModbusDataClient()
        await modbus_client.connect()
        # 데이터 업데이트 태스크 시작
        asyncio.create_task(modbus_client.update_client_data())
        logger.info("Modbus client started")
    except Exception as e:
        logger.error(f"Startup error: {e}")

# Lifespan 컨텍스트 관리자 사용
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 실행
    await startup()
    yield
    # 종료 시 실행
    await shutdown()

# FastAPI 앱 생성 시 lifespan 전달
app = FastAPI(
    title="Stocker Web Server",
    description="Stocker Monitoring System",
    lifespan=lifespan
)

# CORS 미들웨어 설정 유지
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #개발 중에는 모든 origin 허용
    # allow_origins=[
    #     "http://127.0.0.1:5173",  # Vue 개발 서버
    # ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
            
@app.websocket("/ws/stocker")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # 연결 상태 모니터링
    client_info = {
        "ip": websocket.client.host,
        "connect_time": datetime.now().isoformat()
    }
    logger.info(f"New client connected: {client_info}")
    
    try:
        await manager.connect(websocket)
        while True:
            try:
                # ModbusClient에서 데이터 가져오기
                if modbus_client:
                    data = await modbus_client.get_data()
                    if data:
                        await websocket.send_json(data)
                await asyncio.sleep(0.5)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    finally:
        await manager.disconnect(websocket)
        
@asynccontextmanager
async def graceful_shutdown(app):
    """애플리케이션의 우아한 종료를 관리하는 컨텍스트 관리자"""
    try:
        yield app
    finally:
        # 여기에 종료 시 정리 작업 추가
        if modbus_client:
            await modbus_client.close()
        logger.info("Application gracefully shut down")

def handle_exit():
    """프로그램 종료 핸들러"""
    logger.info("Shutdown requested. Cleaning up...")
    sys.exit(0)

async def shutdown():
    """애플리케이션 종료 시 실행될 코드"""
    global modbus_client
    try:
        if modbus_client:
            await modbus_client.close()
        logger.info("Modbus client and resources cleaned up")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    # 현재 이벤트 루프 중지
    loop = asyncio.get_event_loop()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    
    for task in tasks:
        task.cancel()
    
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(
            "stocker_web_server:app", 
            host="0.0.0.0",
            port=5100,      # 포트 5100으로 변경
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server startup error: {e}")