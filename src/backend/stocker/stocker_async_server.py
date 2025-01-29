import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # src/backend를 Python 경로에 추가

from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import logging
import asyncio, time, json, datetime
import os
from logging.handlers import TimedRotatingFileHandler
from pymodbus.device import ModbusDeviceIdentification
from common.db_manager import DBManager
from typing import Dict, Any


# 로그 디렉토리 설정
log_dir = "./log"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "stocker_server.log")

# 로깅 설정
log_handler = TimedRotatingFileHandler(
    log_file, when="M", interval=1, backupCount=10
)
log_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
log_handler.setLevel(logging.INFO)

# 로거 설정
logger = logging.getLogger("StockerLogger")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(logging.StreamHandler())

# Custom Data Block 클래스
class CustomModbusSequentialDataBlock(ModbusSequentialDataBlock):
    def __init__(self, address, values):
        super().__init__(address, values)
        self.last_log_time = 0
        self.LOG_INTERVAL = 1
        self._buffer = []
        # DBManager 초기화 (stocker 타입으로)
        self.db_manager = DBManager('stocker')
        self.retry_count = 3  # DB 저장 재시도 횟수
        self.setup_logging()

    def setValues(self, address, values):
        self._buffer.append((address, values))
        super().setValues(address, values)

        current_time = time.time()
        if current_time - self.last_log_time >= self.LOG_INTERVAL:
            if self._buffer:
                self.last_log_time = current_time
                self.log_all_data()
                self._buffer.clear()

    def setup_logging(self):
        """로깅 설정"""
        log_dir = Path("./log")
        log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger("StockerServer")
        self.logger.setLevel(logging.INFO)
        
        # 파일 핸들러
        fh = logging.FileHandler("./log/stocker_server.log")
        fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
        self.logger.addHandler(fh)
        
        # 콘솔 핸들러
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
        self.logger.addHandler(ch)

    def validate_plc_data(self, values: list) -> bool:
        """PLC 데이터 유효성 검사"""
        try:
            # 기본 길이 확인
            if len(values) < 120:
                self.logger.error(f"Invalid PLC data length: {len(values)}")
                return False

            # 주요 값들의 범위 확인
            validations = [
                (0 < values[0] <= 10, "Bunker ID out of range"),
                (0 < values[1] <= 10, "Stocker ID out of range"),
                (0 <= values[8] <= 500, "Alarm code out of range"),
                (0 <= values[10] <= 1000, "X position out of range"),
                (0 <= values[11] <= 1000, "Z position out of range")
            ]

            for condition, error_msg in validations:
                if not condition:
                    self.logger.error(f"Data validation error: {error_msg}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Data validation error: {str(e)}")
            return False

    async def save_to_db_with_retry(self, equipment_data: Dict[str, Any]) -> bool:
        """DB 저장 재시도 로직"""
        for attempt in range(self.retry_count):
            try:
                stocker_id = str(equipment_data['plc_data']['stocker_id'])
                
                # 두 포트 데이터를 한 번에 저장
                await self.db_manager.update_data(
                    stocker_id=stocker_id,
                    data=equipment_data  # 전체 데이터를 한 번에 저장
                )
                self.logger.info("Data successfully saved to DB")
                return True
            except Exception as e:
                self.logger.error(f"DB save attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.retry_count - 1:
                    await asyncio.sleep(1)  # 재시도 전 대기
                continue
        return False

    def format_equipment_data(self, values: list, bit_values: list, current_time: str) -> Dict[str, Any]:
        """장비 데이터 포맷팅"""
        try:
            # 입력 데이터 복사
            values = list(values)
            bit_values = list(bit_values)
            
            plc_data = {
                'bunker_id': values[0],         # Bunker ID
                'stocker_id': values[1],        # Stocker ID
                'gas_types': values[2:7].copy(),# Gas Stocker 가스 종류
                'alarm_code': values[8],        # Stocker Alarm Code
                'axis_data': {
                    'x_position': values[10],   # X축 현재값
                    'z_position': values[11],   # Z축 현재값
                    'cap_remove_torque': values[12],    # Cap Unit 축 보호캡 분리 Torque 설정값
                    'cap_set_torque': values[13]        # Cap Unit 축 보호캡 체결 Torque 설정값
                },
                'barcodes': {
                    'port_a': ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' 
                                    for i in range(30, 60)]),
                    'port_b': ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' 
                                    for i in range(60, 90)])
                },
                'port_gas_types': {
                    'port_a': values[90:95].copy(),  # [A] Port 가스 종류
                    'port_b': values[95:100].copy()  # [B] Port 가스 종류
                }
            }

            bit_data = {
                'basic_signals': dict(  # Word 100
                    emg_signal=bool(bit_values[0] & (1 << 0)),
                    heart_bit=bool(bit_values[0] & (1 << 1)),
                    run_stop=bool(bit_values[0] & (1 << 2)),
                    server_connected=bool(bit_values[0] & (1 << 3)),
                    t_lamp_red=bool(bit_values[0] & (1 << 4)),
                    t_lamp_yellow=bool(bit_values[0] & (1 << 5)),
                    t_lamp_green=bool(bit_values[0] & (1 << 6)),
                    touch_manual=bool(bit_values[0] & (1 << 7))
                ),
                'door_status': dict(  # Word 105
                    port_a_cylinder=bool(bit_values[5] & (1 << 0)),
                    port_b_cylinder=bool(bit_values[5] & (1 << 1)),
                    port_a_worker_door_open=bool(bit_values[5] & (1 << 2)),
                    port_a_worker_door_close=bool(bit_values[5] & (1 << 3)),
                    port_a_bunker_door_open=bool(bit_values[5] & (1 << 4)),
                    port_a_bunker_door_close=bool(bit_values[5] & (1 << 5)),
                    port_b_worker_door_open=bool(bit_values[5] & (1 << 6)),
                    port_b_worker_door_close=bool(bit_values[5] & (1 << 7)),
                    port_b_bunker_door_open=bool(bit_values[5] & (1 << 8)),
                    port_b_bunker_door_close=bool(bit_values[5] & (1 << 9))
                ),
                'port_a_status': {  # Word 110
                    f'signal_{i}': bool(bit_values[10] & (1 << i))
                    for i in range(16)
                },
                'port_a_detail': {  # Word 111
                    f'signal_{i}': bool(bit_values[11] & (1 << i))
                    for i in range(10)
                },
                'port_b_status': {  # Word 115
                    f'signal_{i}': bool(bit_values[15] & (1 << i))
                    for i in range(16)
                },
                'port_b_detail': {  # Word 116
                    f'signal_{i}': bool(bit_values[16] & (1 << i))
                    for i in range(10)
                }
            }

            return {
                'plc_data': dict(plc_data),  # 전체 데이터도 새로운 딕셔너리로 복사
                'bit_data': dict(bit_data),
                'timestamp': current_time
            }
        except Exception as e:
            self.logger.error(f"Error formatting equipment data: {str(e)}")
            raise

    def log_all_data(self):
        """모든 데이터 로깅"""
        with open("./log/stocker_server.log", "a") as f:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # PLC 데이터 영역
            f.write(f"{current_time} | =========Stocker plc_data 시작 =========\n")
            values = self.getValues(1, 120)  # 주소 1부터 읽기
            
            # DB에 저장할 데이터 구조화
            plc_data = {
                'bunker_id': values[0],
                'stocker_id': values[1],
                'gas_types': values[2:7],
                'alarm_code': values[8],
                'axis_data': {
                    'x_position': values[10],
                    'z_position': values[11],
                    'cap_remove_torque': values[12],
                    'cap_set_torque': values[13]
                },
                'barcodes': {
                    'port_a': ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' 
                                     for i in range(30, 60)]),
                    'port_b': ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' 
                                     for i in range(60, 90)])
                },
                'port_gas_types': {
                    'port_a': values[90:95],
                    'port_b': values[95:100]
                }
            }

            # 비트 데이터 영역
            bit_values = self.getValues(100, 18)
            bit_data = {
                'basic_signals': {
                    'emg_signal': bool(bit_values[0] & (1 << 0)),
                    'heart_bit': bool(bit_values[0] & (1 << 1)),
                    'run_stop': bool(bit_values[0] & (1 << 2)),
                    'server_connected': bool(bit_values[0] & (1 << 3)),
                    't_lamp_red': bool(bit_values[0] & (1 << 4)),
                    't_lamp_yellow': bool(bit_values[0] & (1 << 5)),
                    't_lamp_green': bool(bit_values[0] & (1 << 6)),
                    'touch_manual': bool(bit_values[0] & (1 << 7))
                },
                'cylinder_door_status': {
                    'porta_cylinder': bool(bit_values[5] & (1 << 0)),
                    'portb_cylinder': bool(bit_values[5] & (1 << 1)),
                    'worker_door_open': bool(bit_values[5] & (1 << 2)),
                    'worker_door_close': bool(bit_values[5] & (1 << 3))
                }
            }

            # 통합 데이터 생성
            equipment_data = {
                'plc_data': plc_data,
                'bit_data': bit_data,
                'timestamp': current_time
            }

            try:
                # DB 저장 (비동기로 처리)
                asyncio.create_task(
                    self.db_manager.update_data(
                        f"stocker_{plc_data['stocker_id']}",  # device_id 형식 수정
                        equipment_data  # 전체 데이터 전달
                    )
                )
            except Exception as e:
                f.write(f"{current_time} | DB 저장 오류: {str(e)}\n")
                self.logger.error(f"DB 저장 실패: {e}", exc_info=True)

            # 기본 정보
            f.write(f"{current_time} | Bunker ID: {values[0]}\n")
            f.write(f"{current_time} | Stocker ID: {values[1]}\n")
            for i in range(2, 7):
                f.write(f"{current_time} | Gas Stocker 가스 종류 {i-1}: {values[i]}\n")

            # X, Z축 및 Torque 값
            f.write(f"{current_time} | Stocker Alarm Code: {values[8]}\n")
            f.write(f"{current_time} | X축 현재값: {values[10]}\n")
            f.write(f"{current_time} | Z축 현재값: {values[11]}\n")
            f.write(f"{current_time} | Cap Unit 축 보호캡 분리 Torque: {values[12]}\n")
            f.write(f"{current_time} | Cap Unit 축 보호캡 체결 Torque: {values[13]}\n")

            # Port A Barcode
            barcode_a = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(30, 60)])
            f.write(f"{current_time} | [A] Port Barcode: {barcode_a}\n")

            # Port B Barcode
            barcode_b = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(60, 90)])
            f.write(f"{current_time} | [B] Port Barcode: {barcode_b}\n")

            # Port 가스 종류
            for i in range(90, 95):
                f.write(f"{current_time} | [A] Port 가스 종류 {i-89}: {values[i]}\n")
            for i in range(95, 100):
                f.write(f"{current_time} | [B] Port 가스 종류 {i-94}: {values[i]}\n")
            
            # 비트 데이터 영역
            f.write(f"{current_time} | ========= bit_data 시작 =========\n")
            bit_values = self.getValues(100, 18)
            
            # Word 100 - 기본 신호
            signals = ["EMG Signal", "Heart Bit", "Run/Stop Signal", "Server Connected Bit",
                        "T-LAMP RED", "T-LAMP YELLOW", "T-LAMP GREEN", "Touch 수동동작中 Signal"]
            for i, name in enumerate(signals):
                value = bool(bit_values[0] & (1 << i))
                f.write(f"{current_time} | {name}: {value}\n")

            # Word 105 - 실린더 및 도어 상태
            cylinder_door = [
                "[A] Port 실린더 유무", "[B] Port 실린더 유무",
                "[A] Worker Door Open", "[A] Worker Door Close",
                "[A] Bunker Door Open", "[A] Bunker Door Close",
                "[B] Worker Door Open", "[B] Worker Door Close",
                "[B] Bunker Door Open", "[B] Bunker Door Close"
            ]
            for i, name in enumerate(cylinder_door):
                value = bool(bit_values[5] & (1 << i))
                f.write(f"{current_time} | {name}: {value}\n")

            # Word 110 - A Port 상태
            a_port_status = [
                "[A] Port 보호캡 분리 완료", "[A] Port 보호캡 체결 완료",
                "[A] Worker Door Open 완료", "[A] Worker Door Close 완료",
                "[A] Worker 투입 Ready", "[A] Worker 투입 Complete",
                "[A] Worker 배출 Ready", "[A] Worker 배출 Comlete",
                "[A] Bunker Door Open 완료", "[A] Bunker Door Close 완료",
                "[A] Bunker 투입 Ready", "[A] Bunker 투입 Complete",
                "[A] Bunker 배출 Ready", "[A] Bunker 배출 Comlete",
                "[A] Cylinder Align 진행중", "[A] Cylinder Align 완료"
            ]
            for i, name in enumerate(a_port_status):
                value = bool(bit_values[10] & (1 << i))
                f.write(f"{current_time} | {name}: {value}\n")

            # Word 111 - A Port 진행상태
            a_port_progress = [
                "[A] Cap Open 진행중", "[A] Cap Close 진행중",
                "[A] Cylinder 위치로 X축 이동중", "[A] Cylinder 위치로 X축 이동완료",
                "[A] Cap 위치 찾는중", "[A] Cylinder Neck 위치 찾는중",
                "[A] Worker door Open 진행중", "[A] Worker door Close 진행중",
                "[A] Bunker door Open 진행중", "[A] Bunker door Close 진행중"
            ]
            for i, name in enumerate(a_port_progress):
                value = bool(bit_values[11] & (1 << i))
                f.write(f"{current_time} | {name}: {value}\n")
                # Word 115 - B Port 상태
            b_port_status = [
                "[B] Port 보호캡 분리 완료", "[B] Port 보호캡 체결 완료",
                "[B] Worker Door Open 완료", "[B] Worker Door Close 완료",
                "[B] Worker 투입 Ready", "[B] Worker 투입 Complete",
                "[B] Worker 배출 Ready", "[B] Worker 배출 Comlete",
                "[B] Bunker Door Open 완료", "[B] Bunker Door Close 완료",
                "[B] Bunker 투입 Ready", "[B] Bunker 투입 Complete",
                "[B] Bunker 배출 Ready", "[B] Bunker 배출 Comlete",
                "[B] Cylinder Align 진행중", "[B] Cylinder Align 완료"
            ]
            for i, name in enumerate(b_port_status):
                value = bool(bit_values[15] & (1 << i))
                f.write(f"{current_time} | {name}: {value}\n")

            # Word 116 - B Port 진행상태
            b_port_progress = [
                "[B] Cap Open 진행중", "[B] Cap Close 진행중",
                "[B] Cylinder 위치로 X축 이동중", "[B] Cylinder 위치로 X축 이동완료",
                "[B] Cap 위치 찾는중", "[B] Cylinder Neck 위치 찾는중",
                "[B] Worker door Open 진행중", "[B] Worker door Close 진행중",
                "[B] Bunker door Open 진행중", "[B] Bunker door Close 진행중"
            ]
            for i, name in enumerate(b_port_progress):
                value = bool(bit_values[16] & (1 << i))
                f.write(f"{current_time} | {name}: {value}\n")

# Custom Slave Context 클래스
class CustomModbusSlaveContext(ModbusSlaveContext):
    def __init__(self):
        super().__init__(
            di=CustomModbusSequentialDataBlock(0, [0]*1000),
            co=CustomModbusSequentialDataBlock(0, [0]*1000),
            hr=CustomModbusSequentialDataBlock(0, [0]*1000),
            ir=CustomModbusSequentialDataBlock(0, [0]*1000)
        )
        self.TIME_SYNC_ADDRESS = 900  # 시간 동기화 주소 정의
        self.update_time()
    
    def update_time(self):
        now = datetime.datetime.now()
        time_values = [
            now.year,   # 900: 년
            now.month,  # 901: 월
            now.day,    # 902: 일
            now.hour,   # 903: 시
            now.minute, # 904: 분
            now.second  # 905: 초
        ]
        # 시간 데이터를 900번지에 저장
        try:
            # 홀딩 레지스터에 시간 데이터 저장
            self.setValues(3, self.TIME_SYNC_ADDRESS, list(time_values.copy()))
            #self.store['hr'].setValues(self.TIME_SYNC_ADDRESS, time_values)
            logger.info(f"시간 동기화 완료: {time_values}")
        except Exception as e:
            logger.error(f"시간 동기화 중 오류 발생: {e}")

# 서버 실행 함수
async def run_server():
    store = CustomModbusSlaveContext()
    context = ModbusServerContext(slaves=store, single=True)

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'Stocker'
    identity.ModelName = 'Stocker Server'
    identity.MajorMinorRevision = '1.0'

    logger.info("Starting Modbus TCP Stocker Server...")
    await StartAsyncTcpServer(
        context=context,
        identity=identity,
        address=("127.0.0.1", 5020)
    )

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
