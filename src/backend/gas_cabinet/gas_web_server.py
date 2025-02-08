from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import asyncio
import json
import os
from typing import Set, Dict
from typing import Any, List, Optional
from contextlib import asynccontextmanager
from pymodbus.client import AsyncModbusTcpClient
from datetime import datetime
from gas_cabinet_alarm_code import gas_cabinet_alarm_code
import uvicorn

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger("GasWebServer")

# HTML 템플릿 (이전과 동일하되 스타일과 기능을 개선)
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Gas Cabinet Monitor</title>
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Gas Cabinet Monitoring System</h1>
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
            const ws = new WebSocket("ws://localhost:5001/ws/gas");
            const status = document.getElementById('connection-status');
            const dataContainer = document.getElementById('data-container');
            const alarmContainer = document.getElementById('alarm-container');
            const alarmMessage = document.getElementById('alarm-message');
            
            function formatData(data) {
                let formatted = {
                    plc_data: {
                        bunker_id: data.plc_data.bunker_id,
                        cabinet_id: data.plc_data.cabinet_id,
                        gas_type: data.plc_data.gas_type,
                        status: data.plc_data.status,
                        sensors: data.plc_data.sensors,
                        heaters: data.plc_data.heaters,
                        port_a: data.plc_data.port_a,
                        port_b: data.plc_data.port_b
                    },
                    bit_data: {
                        basic_signals: data.bit_data.word_100.states,
                        av_status: data.bit_data.word_101.states,
                        heater_status: data.bit_data.word_102.states,
                        port_operations: data.bit_data.word_103.states,
                        port_status: data.bit_data.word_105.states,
                        port_a_sequence: data.bit_data.word_110.states,
                        port_a_status: data.bit_data.word_111.states,
                        port_b_sequence: data.bit_data.word_115.states,
                        port_b_status: data.bit_data.word_116 ? data.bit_data.word_116.states : {},
                        port_b_complete: data.bit_data.word_117 ? data.bit_data.word_117.states : {}
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
                    
                    console.log('Original data:', data);  // 원본 데이터 확인
                    
                    // 일단 간단히 포맷팅해서 확인
                    const formattedData = formatData(data);
                    console.log('Formatted data:', formattedData);  // 포맷팅된 데이터 확인
                    
                    dataContainer.textContent = JSON.stringify(formattedData, null, 2);
                    
                    // 알람 처리
                    if (data.plc_data && data.plc_data.status && data.plc_data.status.alarm_code > 0) {
                        alarmContainer.style.display = 'block';
                        alarmMessage.textContent = data.plc_data.status.alarm_message;
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
                // 자동 재연결 시도
                setTimeout(() => {
                    ws = new WebSocket("ws://localhost:5001/ws");
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
                    ws = new WebSocket("ws://localhost:5001/ws");
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
                    self.client = AsyncModbusTcpClient('127.0.0.1', port=5020)
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
                # PLC 데이터 읽기 (기존 코드 유지)
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

                # bit_data도 holding register로 읽기 (수정된 부분)
                bit_results = await self.client.read_holding_registers(
                    address=100,    # 시작 주소
                    count=18,       # 18개 word (100-117)
                    slave=1
                )
                
                if not bit_results or bit_results.isError():
                    logger.error("비트 데이터 읽기 실패")
                    return None

                bit_values = bit_results.registers

                # 데이터 변환 로직
                current_data = {
                    # plc_data 부분은 유지
                    "plc_data": {
                        "bunker_id": results[0] if len(results) > 0 else 0,
                        "cabinet_id": results[1] if len(results) > 1 else 0,
                        "gas_type": results[2:7] if len(results) > 6 else [0]*5,
                        "status": {
                            "machine_code": results[7] if len(results) > 7 else 0,
                            "alarm_code": results[8] if len(results) > 8 else 0,
                            "alarm_message": gas_cabinet_alarm_code.get_description(results[8] if len(results) > 8 else 0)
                        },
                        "sensors": {
                            "pt1a": results[10] if len(results) > 10 else 0,
                            "pt2a": results[11] if len(results) > 11 else 0,
                            "pt1b": results[12] if len(results) > 12 else 0,
                            "pt2b": results[13] if len(results) > 13 else 0,
                            "pt3": results[14] if len(results) > 14 else 0,
                            "pt4": results[15] if len(results) > 15 else 0,
                            "weight_a": results[16] if len(results) > 16 else 0,
                            "weight_b": results[17] if len(results) > 17 else 0
                        },
                        "heaters": {
                            "jacket_heater_a": results[18] if len(results) > 18 else 0,
                            "line_heater_a": results[19] if len(results) > 19 else 0,
                            "jacket_heater_b": results[20] if len(results) > 20 else 0,
                            "line_heater_b": results[21] if len(results) > 21 else 0
                        },
                        "port_a": {
                            "cga_torque": results[24] if len(results) > 24 else 0,
                            "cap_torque": results[25] if len(results) > 25 else 0,
                            "cylinder_position": results[26] if len(results) > 26 else 0,
                            "barcode": ''.join([chr(x) if 32 <= x <= 126 else '?' for x in results[30:60]]),
                            "gas_type": results[90:95] if len(results) > 94 else [0]*5
                        },
                        "port_b": {
                            "cga_torque": results[27] if len(results) > 27 else 0,
                            "cap_torque": results[28] if len(results) > 28 else 0,
                            "cylinder_position": results[29] if len(results) > 29 else 0,
                            "barcode": ''.join([chr(x) if 32 <= x <= 126 else '?' for x in results[60:90]]),
                            "gas_type": results[95:100] if len(results) > 99 else [0]*5
                        }
                    },
                    # bit_data 부분 수정 (word 단위로 비트 연산)
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
                        "word_101": {
                            "raw": bit_values[1],
                            "states": {
                                "AV1A": bool(bit_values[1] & (1 << 0)),
                                "AV2A": bool(bit_values[1] & (1 << 1)),
                                "AV3A": bool(bit_values[1] & (1 << 2)),
                                "AV4A": bool(bit_values[1] & (1 << 3)),
                                "AV5A": bool(bit_values[1] & (1 << 4)),
                                "AV1B": bool(bit_values[1] & (1 << 5)),
                                "AV2B": bool(bit_values[1] & (1 << 6)),
                                "AV3B": bool(bit_values[1] & (1 << 7)),
                                "AV4B": bool(bit_values[1] & (1 << 8)),
                                "AV5B": bool(bit_values[1] & (1 << 9)),
                                "AV7": bool(bit_values[1] & (1 << 10)),
                                "AV8": bool(bit_values[1] & (1 << 11)),
                                "AV9": bool(bit_values[1] & (1 << 12))
                            }
                        },
                        "word_102": {
                            "raw": bit_values[2],
                            "states": {
                                "JACKET HEATER A RELAY": bool(bit_values[2] & (1 << 0)),
                                "LINE HEATER A RELAY": bool(bit_values[2] & (1 << 1)),
                                "JACKET HEATER B RELAY": bool(bit_values[2] & (1 << 2)),
                                "LINE HEATER B RELAY": bool(bit_values[2] & (1 << 3)),
                                "GAS LEAK SHUT DOWN": bool(bit_values[2] & (1 << 4)),
                                "VMB STOP SIGNAL": bool(bit_values[2] & (1 << 5)),
                                "UV/IR SENSOR": bool(bit_values[2] & (1 << 6)),
                                "HIGH TEMP SENSOR": bool(bit_values[2] & (1 << 7)),
                                "SMOKE SENSOR": bool(bit_values[2] & (1 << 8))
                            }
                        },
                        "word_103": {
                            "raw": bit_values[3],
                            "states": {
                                "[A] Port Insert Request": bool(bit_values[3] & (1 << 0)),
                                "[A] Port Insert Complete": bool(bit_values[3] & (1 << 1)),
                                "[A] Port Remove Request": bool(bit_values[3] & (1 << 2)),
                                "[A] Port Remove Complete": bool(bit_values[3] & (1 << 3)),
                                "[B] Port Insert Request": bool(bit_values[3] & (1 << 8)),
                                "[B] Port Insert Complete": bool(bit_values[3] & (1 << 9)),
                                "[B] Port Remove Request": bool(bit_values[3] & (1 << 10)),
                                "[B] Port Remove Complete": bool(bit_values[3] & (1 << 11))
                            }
                        },
                        "word_105": {
                            "raw": bit_values[5],
                            "states": {
                                "[A] Port 실린더 유무": bool(bit_values[5] & (1 << 0)),
                                "[B] Port 실린더 유무": bool(bit_values[5] & (1 << 1)),
                                "Door Open 완료": bool(bit_values[5] & (1 << 2)),
                                "Door Close 완료": bool(bit_values[5] & (1 << 3))
                            }
                        },
                        "word_110": {
                            "raw": bit_values[10],
                            "states": {
                                "[A] Close the Cylinder": bool(bit_values[10] & (1 << 0)),
                                "[A] 1st Purge before Exchange": bool(bit_values[10] & (1 << 1)),
                                "[A] Decompression Test": bool(bit_values[10] & (1 << 2)),
                                "[A] 2nd Purge before Exchange": bool(bit_values[10] & (1 << 3)),
                                "[A] Exchange Cylinder": bool(bit_values[10] & (1 << 4)),
                                "[A] 1st Purge after Exchange": bool(bit_values[10] & (1 << 5)),
                                "[A] Pressure Test": bool(bit_values[10] & (1 << 6)),
                                "[A] 2nd Purge after Exchange": bool(bit_values[10] & (1 << 7)),
                                "[A] Purge Completed": bool(bit_values[10] & (1 << 8)),
                                "[A] Prepare to Supply": bool(bit_values[10] & (1 << 9)),
                                "[A] Gas Supply AV3 Open/Close Choose": bool(bit_values[10] & (1 << 10)),
                                "[A] Gas Supply": bool(bit_values[10] & (1 << 11)),
                                "[A] Ready to Supply": bool(bit_values[10] & (1 << 12))
                            }
                        },
                        "word_111": {
                            "raw": bit_values[11],
                            "states": {
                                "[A] Cyclinder Ready": bool(bit_values[11] & (1 << 0)),
                                "[A] CGA Disconnect Complete": bool(bit_values[11] & (1 << 1)),
                                "[A] CGA Connect Complete": bool(bit_values[11] & (1 << 2)),
                                "[A] Cylinder Valve Open Complete": bool(bit_values[11] & (1 << 3)),
                                "[A] Cylinder Valve Close Complete": bool(bit_values[11] & (1 << 4)),
                                "[A] Cylinder Valve Open Status": bool(bit_values[11] & (1 << 5)),
                                "[A] Cylinder Lift Unit Ready": bool(bit_values[11] & (1 << 6)),
                                "[A] Cylinder Lift Unit Moving Up": bool(bit_values[11] & (1 << 7)),
                                "[A] Cylinder Lift Unit Moving Down": bool(bit_values[11] & (1 << 8)),
                                "[A] CGA Separation In Progress": bool(bit_values[11] & (1 << 9)),
                                "[A] CGA Connection In Progress": bool(bit_values[11] & (1 << 10)),
                                "[A] Cylinder Cap Separation In Progress": bool(bit_values[11] & (1 << 11)),
                                "[A] Cylinder Valve Open In Progress": bool(bit_values[11] & (1 << 12)),
                                "[A] Cylinder Valve Close In Progress": bool(bit_values[11] & (1 << 13)),
                                "[A] Cylinder Alignment In Progress": bool(bit_values[11] & (1 << 14)),
                                "[A] Cylinder Turn In Progress": bool(bit_values[11] & (1 << 15))
                            }
                        },
                        "word_115": {
                            "raw": bit_values[15],
                            "states": {
                                "[B] Close the Cylinder": bool(bit_values[15] & (1 << 0)),
                                "[B] 1st Purge before Exchange": bool(bit_values[15] & (1 << 1)),
                                "[B] Decompression Test": bool(bit_values[15] & (1 << 2)),
                                "[B] 2nd Purge before Exchange": bool(bit_values[15] & (1 << 3)),
                                "[B] Exchange Cylinder": bool(bit_values[15] & (1 << 4)),
                                "[B] 1st Purge after Exchange": bool(bit_values[15] & (1 << 5)),
                                "[B] Pressure Test": bool(bit_values[15] & (1 << 6)),
                                "[B] 2nd Purge after Exchange": bool(bit_values[15] & (1 << 7)),
                                "[B] Purge Completed": bool(bit_values[15] & (1 << 8)),
                                "[B] Prepare to Supply": bool(bit_values[15] & (1 << 9)),
                                "[B] Gas Supply AV3 Open/Close Choose": bool(bit_values[15] & (1 << 10)),
                                "[B] Gas Supply": bool(bit_values[15] & (1 << 11)),
                                "[B] Ready to Supply": bool(bit_values[15] & (1 << 12))
                            }
                        },
                        "word_116": {
                            "raw": bit_values[16],
                            "states": {
                                "[B] Cylinder Ready": bool(bit_values[16] & (1 << 0)),
                                "[B] CGA Disconnect Complete": bool(bit_values[16] & (1 << 1)),
                                "[B] CGA Connect Complete": bool(bit_values[16] & (1 << 2)),
                                "[B] Cylinder Valve Open Complete": bool(bit_values[16] & (1 << 3)),
                                "[B] Cylinder Valve Close Complete": bool(bit_values[16] & (1 << 4)),
                                "[B] Cylinder Valve Open Status": bool(bit_values[16] & (1 << 5)),
                                "[B] Cylinder Lift Unit Ready": bool(bit_values[16] & (1 << 6)),
                                "[B] Cylinder Lift Unit Moving Up": bool(bit_values[16] & (1 << 7)),
                                "[B] Cylinder Lift Unit Moving Down": bool(bit_values[16] & (1 << 8)),
                                "[B] CGA Separation In Progress": bool(bit_values[16] & (1 << 9)),
                                "[B] CGA Connection In Progress": bool(bit_values[16] & (1 << 10)),
                                "[B] Cylinder Cap Separation In Progress": bool(bit_values[16] & (1 << 11)),
                                "[B] Cylinder Valve Open In Progress": bool(bit_values[16] & (1 << 12)),
                                "[B] Cylinder Valve Close In Progress": bool(bit_values[16] & (1 << 13)),
                                "[B] Cylinder Alignment In Progress": bool(bit_values[16] & (1 << 14)),
                                "[B] Cylinder Turn In Progress": bool(bit_values[16] & (1 << 15))
                            }
                        },
                        "word_117": {
                            "raw": bit_values[17],
                            "states": {
                                "[B] Cylinder Turn Complete": bool(bit_values[17] & (1 << 0)),
                                "[B] Cylinder Clamp Complete": bool(bit_values[17] & (1 << 1)),
                                "[B] CGA Connect Complete Status": bool(bit_values[17] & (1 << 2))
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
                data = await self.get_data()
                if data:
                    await manager.broadcast(data)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"데이터 업데이트 오류: {e}")
                await asyncio.sleep(1)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.socket_path = '/tmp/cabinet_data.sock'
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
        asyncio.create_task(modbus_client.update_client_data())
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
    title="Gas Cabinet Web Server",
    description="Gas Cabinet Monitoring System"
)
# 대신 이것으로 교체
#router = APIRouter()

# CORS 미들웨어 설정 삭제
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

@app.on_event("startup")
async def on_startup():
    await startup()

@app.on_event("shutdown")
async def on_shutdown():
    await shutdown()    

@app.get("/", response_class=HTMLResponse)
async def get():
    return html

@app.websocket("/ws/gas")
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
            "gas_web_server:app",  # 이 부분이 중요: 모듈:app 형식으로 지정
            host="0.0.0.0",
            port=5002,             # WebSocket 전용 포트로 변경 권장
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Server startup error: {e}")