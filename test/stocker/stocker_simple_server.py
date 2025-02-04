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
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from common.db_manager import DBManager
from typing import Dict, Any
from stocker_alarm_codes import stocker_alarm_code

# 로그 디렉토리 설정
log_dir = "./log"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "stocker_server.log")

# 로거 설정
logger = logging.getLogger("StockerLogger")
logger.setLevel(logging.INFO)

# 로거의 핸들러 중복 방지
if not logger.handlers:
    log_handler = TimedRotatingFileHandler(
        log_file, when="M", interval=1, backupCount=10
    )
    log_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
    log_handler.setLevel(logging.INFO)

    # 로거 설정
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
        """장비 데이터 포맷팅 - 간소화된 버전"""
        try:
            plc_data = {
                'bunker_id': values[0],
                'stocker_id': values[1],
                'alarm_code': values[8],
                'axis_data': {
                    'x_position': values[10],
                    'z_position': values[11]
                },
                'barcodes': {
                    'port_a': ''.join([chr(values[i]) if 32 <= values[i] <= 126 else '' for i in range(30, 60)]).strip(),
                    'port_b': ''.join([chr(values[i]) if 32 <= values[i] <= 126 else '' for i in range(60, 90)]).strip()
                }
            }

            bit_data = {
                'basic_signals': {
                    'emg_signal': bool(bit_values[0] & (1 << 0)),
                    'heart_bit': bool(bit_values[0] & (1 << 1)),
                    'run_stop': bool(bit_values[0] & (1 << 2)),
                    'server_connected': bool(bit_values[0] & (1 << 3))
                },
                'door_status': {
                    'port_a_cylinder': bool(bit_values[5] & (1 << 0)),
                    'port_b_cylinder': bool(bit_values[5] & (1 << 1))
                }
            }

            return {
                'plc_data': plc_data,
                'bit_data': bit_data,
                'timestamp': current_time
            }
        except Exception as e:
            self.logger.error(f"Error formatting equipment data: {str(e)}")
            raise

def log_all_data(self):
    """모든 데이터 로깅 - 간소화된 버전"""
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    values = self.getValues(1, 120)
    bunker_id = values[0]
    stocker_id = values[1]

    if bunker_id <= 0 or stocker_id <= 0:
        return  # 유효하지 않은 ID는 건너뜀

    try:
        with open("./log/stocker_server.log", "a") as f:
            # 최소한의 핵심 정보만 로깅
            f.write(f"{current_time} | Bunker ID: {bunker_id}, Stocker ID: {stocker_id}\n")
            f.write(f"{current_time} | Alarm Code: {values[8]}\n")
            f.write(f"{current_time} | X-Axis Position: {values[10]}, Z-Axis Position: {values[11]}\n")
            
            # 바코드 정보 (간소화)
            barcode_a = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else '' for i in range(30, 60)]).strip()
            barcode_b = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else '' for i in range(60, 90)]).strip()
            f.write(f"{current_time} | Barcodes - A: {barcode_a}, B: {barcode_b}\n")

            # 비트 데이터 핵심 상태만 로깅
            bit_values = self.getValues(100, 18)
            f.write(f"{current_time} | Emergency Signal: {bool(bit_values[0] & (1 << 0))}\n")
            f.write(f"{current_time} | Server Connected: {bool(bit_values[0] & (1 << 3))}\n")

            # 장비 데이터 생성 및 DB 저장
            equipment_data = {
                'plc_data': {
                    'bunker_id': bunker_id,
                    'stocker_id': stocker_id,
                    'alarm_code': values[8],
                    'x_position': values[10],
                    'z_position': values[11],
                    'barcodes': {
                        'port_a': barcode_a,
                        'port_b': barcode_b
                    }
                },
                'timestamp': current_time
            }

            # DB 저장 (필요한 경우에만)
            if bunker_id > 0 and stocker_id > 0:
                asyncio.create_task(
                    self.db_manager.update_data(
                        f"stocker_{stocker_id}",
                        equipment_data
                    )
                )

            # 알람 코드 처리 (간소화)
            if values[8] > 0:
                asyncio.create_task(
                    self.db_manager.save_alarm(
                        f"stocker_{stocker_id}", 
                        values[8], 
                        f"Stocker {stocker_id} Alarm"
                    )
                )

    except Exception as e:
        self.logger.error(f"Logging error: {e}", exc_info=True)

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
        address=("127.0.0.1", 5021)
    )

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")