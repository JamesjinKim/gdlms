import sys
from pathlib import Path
from typing import Set
sys.path.append(str(Path(__file__).parent.parent))
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import logging
import socket
from gas_cabinet_alarm_code import gas_cabinet_alarm_code
from logging.handlers import TimedRotatingFileHandler
import asyncio, time, json, datetime
import os
from pymodbus.device import ModbusDeviceIdentification
from copy import deepcopy
import gc
from common.db_manager import DBManager

# 로그 디렉토리 생성 및 설정
log_dir = "./log"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "gas_cabinet.log")

# 로깅 설정
log_handler = TimedRotatingFileHandler(
    log_file, when="M", interval=1, backupCount=10
)
log_handler.suffix = "%Y%m%d%H%M"
log_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
log_handler.setLevel(logging.INFO)

# 로거 설정
logger = logging.getLogger("GasCabinetLogger")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(logging.StreamHandler())

class CustomModbusSequentialDataBlock(ModbusSequentialDataBlock):
    def __init__(self, address, values):
        super().__init__(address, values)
        self.last_log_time = 0
        self.LOG_INTERVAL = 1
        self._buffer = []
        # DBManager 인스턴스 생성
        self.db_manager = DBManager('gas_cabinet')
        self.retry_count = 3  # DB 저장 재시도 횟수

    def setValues(self, address, values):
        self._buffer.append((address, deepcopy(values)))
        super().setValues(address, values)
        
        current_time = time.time()
        if current_time - self.last_log_time >= self.LOG_INTERVAL:
            if self._buffer:
                self.last_log_time = current_time
                self.log_all_data()
                self._buffer.clear()
                gc.collect()
    
    def format_data_for_db(self, values):
        """DB 저장을 위한 데이터 포맷팅"""
        try:
            # 바코드 데이터 처리
            barcode_a = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(30, 60)]).strip()
            barcode_b = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(60, 90)]).strip()
            
            # 비트 데이터 읽기
            bit_values = self.getValues(100, 18)

            # 비트 데이터를 true/false 딕셔너리로 변환하는 함수
            def word_to_bool_dict(word, max_bits=16):
                return {
                    f'bit_{i}': bool(word & (1 << i)) 
                    for i in range(max_bits)
                }

            # 데이터 구조화
            status_data = {
                "plc_data": {
                    "bunker_id": values[0],
                    "gas_cabinet_id": values[1],
                    "alarm_code": values[8],
                    "sensors": {
                        "pressure": [values[10], values[11], values[12], values[13], values[14], values[15]],
                        "weight": [values[16], values[17]]
                    },
                    "heaters": [
                        values[18], values[19],  # port_a jacket, line
                        values[20], values[21]   # port_b jacket, line
                    ],
                    "barcodes": {
                        "port_a": barcode_a,
                        "port_b": barcode_b
                    }
                },
                "bit_data": {
                    f"word_{100+i}": word_to_bool_dict(bit_values[i]) 
                    for i in range(18)
                }
            }
            
            return status_data
                
        except Exception as e:
            logger.error(f"Data formatting error: {e}")
            return None

    def log_all_data(self):
        """모든 데이터 로깅"""
        with open("./log/gas_cabinet.log", "a") as f:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # PLC 데이터 영역
            values = self.getValues(1, 120)  # 주소 1부터 읽기
            
            # 기본 데이터 유효성 검사
            bunker_id = values[0]
            gas_cabinet_id = values[1]
            
            if bunker_id > 0 and gas_cabinet_id > 0:
                try:
                    # 비트 데이터 읽기
                    bit_values = self.getValues(100, 18)

                    # 비트 데이터를 true/false 딕셔너리로 변환하는 함수
                    def word_to_bool_dict(word, max_bits=16):
                        return {
                            f'bit_{i}': bool(word & (1 << i)) 
                            for i in range(max_bits)
                        }

                    # 통합 데이터
                    equipment_data = {
                        'plc_data': {
                            'bunker_id': values[0],
                            'gas_cabinet_id': values[1],
                            'alarm_code': values[8],
                            'sensors': {
                                'pressure': [values[10], values[11], values[12], values[13], values[14], values[15]],
                                'weight': [values[16], values[17]]
                            },
                            'heaters': [
                                values[18], values[19],  # port_a jacket, line
                                values[20], values[21]   # port_b jacket, line
                            ],
                            'barcodes': {
                                'port_a': ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(30, 60)]).strip(),
                                'port_b': ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(60, 90)]).strip()
                            }
                        },
                        'bit_data': {
                            f"word_{100+i}": word_to_bool_dict(bit_values[i]) 
                            for i in range(18)
                        },
                        'timestamp': current_time
                    }

                    # DB 저장 작업
                    asyncio.create_task(
                        self.db_manager.update_data(
                            f"gas_{gas_cabinet_id}",
                            equipment_data
                        )
                    )

                    # 로그 파일에 데이터 기록
                    f.write(f"{current_time} | =========Gas Cabinet plc_data 시작 =========\n")
                    f.write(f"{current_time} | Bunker ID: {values[0]}\n")
                    f.write(f"{current_time} | Gas Cabinet ID: {values[1]}\n")
                    
                    # 기본 센서 및 상태 정보 로깅
                    f.write(f"{current_time} | 압력 센서 값: {equipment_data['plc_data']['sensors']['pressure']}\n")
                    f.write(f"{current_time} | 무게 센서 값: {equipment_data['plc_data']['sensors']['weight']}\n")
                    f.write(f"{current_time} | 히터 상태: {equipment_data['plc_data']['heaters']}\n")
                    
                    # 비트 데이터 로깅
                    f.write(f"{current_time} | ========= Bit Data 시작 =========\n")
                    for word, bits in equipment_data['bit_data'].items():
                        f.write(f"{current_time} | {word}: {bits}\n")

                except Exception as e:
                    f.write(f"{current_time} | DB 저장 오류: {str(e)}\n")
                    logger.error(f"DB 저장 실패: {e}", exc_info=True)

class CustomModbusSlaveContext(ModbusSlaveContext):
    def __init__(self):
        # 메모리 초기화
        gc.collect()
        
        # 각 데이터 블록 초기화
        values = [0] * 1000
        di_values = deepcopy(values)
        co_values = deepcopy(values)
        hr_values = deepcopy(values)
        ir_values = deepcopy(values)
        
        super().__init__(
            di=CustomModbusSequentialDataBlock(0, di_values),
            co=CustomModbusSequentialDataBlock(0, co_values),
            hr=CustomModbusSequentialDataBlock(0, hr_values),
            ir=CustomModbusSequentialDataBlock(0, ir_values)
        )
        
        self.TIME_SYNC_ADDRESS = 900
        
        # 메모리 정리 및 시간 동기화
        gc.collect()
        self.update_time()

    def update_time(self):
        """현재 시간을 레지스터에 업데이트"""
        now = datetime.datetime.now()
        time_values = [
            now.year,   # 900: 년
            now.month,  # 901: 월
            now.day,    # 902: 일
            now.hour,   # 903: 시
            now.minute, # 904: 분
            now.second  # 905: 초
        ]
        self.setValues(3, self.TIME_SYNC_ADDRESS, deepcopy(time_values))
        logger.info(f"시간 동기화 데이터 업데이트: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        gc.collect()
            
# 서버 실행 함수
async def run_server():
    """서버 실행 함수"""
    store = CustomModbusSlaveContext()
    context = ModbusServerContext(slaves=store, single=True)

    # Modbus 장치 식별 정보 설정
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'GasCabinet'
    identity.ModelName = 'GasCabinet Server'
    identity.MajorMinorRevision = '1.0'
    
    logger.info("Starting Modbus TCP Gas Cabinet Server...")
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