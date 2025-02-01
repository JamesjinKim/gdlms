from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import asyncio
import os
import json
from typing import List, Dict, Optional
from contextlib import asynccontextmanager
from pymodbus.client import AsyncModbusTcpClient
from stocker_alarm_codes import stocker_alarm_code
import uvicorn

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger("StockerWebServer")

# HTML 템플릿 (이전과 동일하되 스타일과 기능을 개선)
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Stocker Monitor</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                margin: 0;
                padding: 20px;
                font-family: Arial, sans-serif;
                background: #f5f5f5;
            }
            .container { 
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                border-bottom: 2px solid #eee;
                padding-bottom: 10px;
            }
            .status {
                margin: 20px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 4px;
                border-left: 4px solid #6c757d;
            }
            .status span {
                font-weight: bold;
            }
            .data-display {
                background: #fff;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 20px;
            }
            .data-display h3 {
                color: #495057;
                margin-top: 0;
            }
            pre {
                white-space: pre-wrap;
                word-wrap: break-word;
                background: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
                border: 1px solid #e9ecef;
                font-family: monospace;
                font-size: 14px;
            }
            .connected { color: #28a745; }
            .disconnected { color: #dc3545; }
            .error { color: #dc3545; }
            
            /* 새로운 스타일 추가 */
            .alarm {
                background-color: #fff3cd;
                border: 1px solid #ffeeba;
                color: #856404;
                padding: 10px;
                margin-top: 10px;
                border-radius: 4px;
                display: none;
            }
            .indicator {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 5px;
            }
            .indicator.on { background-color: #28a745; }
            .indicator.off { background-color: #dc3545; }

            .bit-data {
                margin-top: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-left: 4px solid #28a745;
            }
            .bit-status {
                display: inline-block;
                margin-right: 10px;
                padding: 2px 6px;
                border-radius: 3px;
                background: #e9ecef;
            }
            .bit-true { color: #28a745; }
            .bit-false { color: #dc3545; }

        </style>
    </head>
    <body>
        <div class="container">
            <h1>Stocker Monitoring System</h1>
            <div class="status">
                Connection Status: <span id="connection-status">Disconnected</span>
            </div>
            <div class="alarm" id="alarm-container">
                <strong>Alarm:</strong> <span id="alarm-message"></span>
            </div>
            <div class="data-display">
                <h3>Real-time Data:</h3>
                <pre id="data-container">Waiting for data...</pre>
            </div>
        </div>

        <script>
            const ws = new WebSocket("ws://localhost:5002/ws/stocker");
            const status = document.getElementById('connection-status');
            const dataContainer = document.getElementById('data-container');
            const alarmContainer = document.getElementById('alarm-container');
            const alarmMessage = document.getElementById('alarm-message');
            
            function formatData(data) {
                let formatted = {
                    plc_data: {
                        bunker_id: data.plc_data.bunker_id,
                        stocker_id: data.plc_data.stocker_id,
                        gas_type: data.plc_data.gas_type,
                        system_status: data.plc_data.system_status,
                        position: data.plc_data.position,
                        torque: data.plc_data.torque,
                        port_a: data.plc_data.port_a,
                        port_b: data.plc_data.port_b
                    },
                    bit_data: {
                        basic_signals: data.bit_data.word_100.states,
                        door_status: data.bit_data.word_105.states,
                        port_a_status: data.bit_data.word_110.states,
                        port_a_progress: data.bit_data.word_111.states,
                        port_b_status: data.bit_data.word_115.states,
                        port_b_progress: data.bit_data.word_116.states
                    }
                };
                return formatted;
            }
            
            ws.onopen = () => {
                console.log('WebSocket connection established');
                status.textContent = 'Connected';
                status.className = 'connected';
            };

            ws.onmessage = (event) => {
                try {
                    const rawData = event.data;                    
                    const data = JSON.parse(rawData);
                    
                    // formatData 함수를 사용하여 데이터 포맷팅
                    const formattedData = formatData(data);
                    dataContainer.textContent = JSON.stringify(formattedData, null, 2);
                    
                    // 알람 처리
                    const alarmCode = data.plc_data.system_status.alarm_code;
                    if (alarmCode > 0) {
                        alarmContainer.style.display = 'block';
                        alarmMessage.textContent = data.plc_data.system_status.alarm_message;
                    } else {
                        alarmContainer.style.display = 'none';
                    }
                } catch (error) {
                    console.error('데이터 처리 중 오류:', error);
                    console.error('받은 원본 데이터:', event.data);                    
                }
            };

            ws.onclose = () => {
                status.textContent = 'Disconnected';
                status.className = 'disconnected';
                setTimeout(() => {
                    ws = new WebSocket("ws://localhost:5002/ws");
                }, 3000);
            };

            ws.onerror = (error) => {
                status.textContent = 'Error';
                status.className = 'error';
                console.error('WebSocket error:', error);
            };
            
            function reconnect() {
                if (ws.readyState === WebSocket.CLOSED) {
                    status.textContent = 'Reconnecting...';
                    ws = new WebSocket("ws://localhost:5002/ws");
                }
            }
            
            // 페이지 종료 시 연결 정리
            window.addEventListener('beforeunload', () => {
                if (ws) {
                    ws.close();
                }
            });
        </script>
    </body>
</html>
"""

class ModbusDataClient:
    def __init__(self):
        self.client = None
        self.connected = False
        self.unit = 1
        self.last_data = None
        self.running = True
        self._lock = asyncio.Lock()
    
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
                        "system_status": {
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

    async def update_client_data(modbus_client):
        while modbus_client.running:  # running 플래그 확인
            try:
                data = await modbus_client.get_data()
                if data:
                    await manager.broadcast(data)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"데이터 업데이트 오류: {e}")
                await asyncio.sleep(1)
    
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        async with self._lock:
            self.active_connections.append(websocket)
            print(f"WebSocket 클라이언트 연결됨. 현재 연결 수: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"WebSocket 클라이언트 연결 해제. 현재 연결 수: {len(self.active_connections)}")

    async def broadcast(self, data: dict):
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(data)
            except Exception as e:
                print(f"브로드캐스트 오류: {e}")
                await self.disconnect(connection)

    async def handle_unix_connection(self, reader, writer):
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                try:
                    json_data = json.loads(data.decode())
                    logger.info(f"Received data from Unix socket: {len(str(json_data))} bytes")
                    await self.broadcast(json_data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON data received: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            
    async def setup_unix_socket(self):
        """유닉스 소켓 서버 설정"""
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        
        self.unix_server = await asyncio.start_unix_server(
            self.handle_unix_connection, 
            self.socket_path
        )
        return self.unix_server        
    
    async def cleanup(self):
        """리소스 정리"""
        if self.unix_server:
            self.unix_server.close()
            await self.unix_server.wait_closed()
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

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
        asyncio.create_task(update_client_data(modbus_client))
        logger.info("Modbus client started")
    except Exception as e:
        logger.error(f"Startup error: {e}")

async def shutdown():
    """애플리케이션 종료 시 실행될 코드"""
    global modbus_client
    if modbus_client:
        await modbus_client.close()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="Stocker Web Server",
    description="Stocker Monitoring System"
)

# CORS 미들웨어 설정 유지
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def on_startup():
    await startup()

@app.on_event("shutdown")
async def on_shutdown():
    await shutdown()    

@app.get("/", response_class=HTMLResponse)
async def get():
    return html
            
@app.websocket("/ws/stocker")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await manager.connect(websocket)
    try:
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
        
if __name__ == "__main__":
    try:
        uvicorn.run(
            "stocker_web_server:app",  # 이 부분이 중요: 모듈:app 형식으로 지정
            host="0.0.0.0",
            port=5002,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Server startup error: {e}")