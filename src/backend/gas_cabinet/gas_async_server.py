from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import logging
import socket
from gas_cabinet_alarm_code import gas_cabinet_alarm_code
from logging.handlers import TimedRotatingFileHandler
import asyncio, time, json, datetime
import os
from logging.handlers import TimedRotatingFileHandler
from pymodbus.device import ModbusDeviceIdentification
from copy import deepcopy
import gc

# 로그 파일 경로 설정
log_dir = "./log"
# 로그 디렉토리 생성
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
        # 메모리 명시적 초기화
        self._values = [0] * len(values)  # 먼저 메모리 할당
        gc.collect()  # 가비지 컬렉션 강제 실행
        
        # deepcopy를 사용하여 새로운 메모리 공간에 값 복사
        self._values = deepcopy([0] * len(values))
        
        super().__init__(address, self._values)
        self.last_log_time = 0
        self.LOG_INTERVAL = 1
        self._buffer = []

    def setValues(self, address, values):
        # 값을 설정하기 전에 메모리 정리
        gc.collect()
        
        # 변경된 데이터를 버퍼에 추가
        self._buffer.append((address, deepcopy(values)))
        super().setValues(address, values)
        
        current_time = time.time()
        if current_time - self.last_log_time >= self.LOG_INTERVAL:
            if self._buffer:  # 버퍼에 데이터가 있는 경우만 로깅
                self.last_log_time = current_time
                self.log_all_data()
                self._buffer.clear()  # 버퍼 초기화
                gc.collect()  # 버퍼 클리어 후 메모리 정리

    def log_all_data(self):
        """모든 데이터 로깅"""
        with open("./log/gas_cabinet.log", "a") as f:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            # PLC 데이터 영역
            f.write(f"{current_time} | =========Gas Cabinet plc_data 시작 =========\n")
            values = self.getValues(1, 120)  # 주소 1부터 읽기

            # 기본 정보
            f.write(f"{current_time} | Bunker ID: {values[0]}\n")
            f.write(f"{current_time} | Gas Cabinet ID: {values[1]}\n")
            for i in range(2, 7):
                f.write(f"{current_time} | Gas Cabinet 가스 종류 {i-1}: {values[i]}\n")

            # 시스템 상태
            f.write(f"{current_time} | Gas Cabinet Alarm Code: {values[8]}\n")
            
            # 센서 데이터
            f.write(f"{current_time} | PT1A: {values[10]} PSI\n")
            f.write(f"{current_time} | PT2A: {values[11]} PSI\n")
            f.write(f"{current_time} | PT1B: {values[12]} PSI\n")
            f.write(f"{current_time} | PT2B: {values[13]} PSI\n")
            f.write(f"{current_time} | PT3: {values[14]} PSI\n")
            f.write(f"{current_time} | PT4: {values[15]} PSI\n")
            f.write(f"{current_time} | WA (A Port Weight): {values[16]} kg\n")
            f.write(f"{current_time} | WB (B Port Weight): {values[17]} kg\n")

            # 히터 상태
            f.write(f"{current_time} | [A] JACKET HEATER: {values[18]}°C\n")
            f.write(f"{current_time} | [A] LINE HEATER: {values[19]}°C\n")
            f.write(f"{current_time} | [B] JACKET HEATER: {values[20]}°C\n")
            f.write(f"{current_time} | [B] LINE HEATER: {values[21]}°C\n")

            # A Port Torque & Position 데이터
            f.write(f"{current_time} | [A] CGA 체결 Torque: {values[24]} kgf·cm\n")
            f.write(f"{current_time} | [A] CAP 체결 Torque: {values[25]} kgf·cm\n")
            f.write(f"{current_time} | [A] 실린더 Up/Down Pos: {values[26]} mm\n")

            # B Port Torque & Position 데이터
            f.write(f"{current_time} | [B] CGA 체결 Torque: {values[27]} kgf·cm\n")
            f.write(f"{current_time} | [B] CAP 체결 Torque: {values[28]} kgf·cm\n")
            f.write(f"{current_time} | [B] 실린더 Up/Down Pos: {values[29]} mm\n")

            # A Port Barcode 데이터
            barcode_a = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(30, 60)])
            f.write(f"{current_time} | [A] Port Barcode: {barcode_a}\n")

            # B Port Barcode 데이터
            barcode_b = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(60, 90)])
            f.write(f"{current_time} | [B] Port Barcode: {barcode_b}\n")

            # Gas Types
            for i in range(90, 95):
                f.write(f"{current_time} | [A] Port 가스 종류 {i-89}: {values[i]}\n")
            for i in range(95, 100):
                f.write(f"{current_time} | [B] Port 가스 종류 {i-94}: {values[i]}\n")

            # 비트 데이터 영역
            f.write(f"{current_time} | ========= Gas Cabinet Bit Area Data 시작 =========\n")
            bit_values = self.getValues(100, 18)  # 100번 주소부터 18개 워드 읽기

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
            b_port_status = [x.replace('[A]', '[B]') for x in a_port_status]
            for i, name in enumerate(b_port_status):
                value = bool(bit_values[15] & (1 << i))
                f.write(f"{current_time} | {name}: {value}\n")

            # Word 116 - B Port 진행상태
            b_port_progress = [x.replace('[A]', '[B]') for x in a_port_progress]
            for i, name in enumerate(b_port_progress):
                value = bool(bit_values[16] & (1 << i))
                f.write(f"{current_time} | {name}: {value}\n")

class CustomModbusSlaveContext(ModbusSlaveContext):
    def __init__(self):
        # 메모리 초기화
        gc.collect()
        
        # 각 데이터 블록에 대한 메모리 공간 생성
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
        
        # 메모리 정리 후 시간 동기화
        gc.collect()
        self.update_time()
    
    def update_time(self):
        """현재 시간을 레지스터에 업데이트 (900-905 주소 사용)"""
        now = datetime.datetime.now()
        time_values = [
            now.year,   # 900: 년
            now.month,  # 901: 월
            now.day,    # 902: 일
            now.hour,   # 903: 시
            now.minute, # 904: 분
            now.second  # 905: 초
        ]
        # deepcopy를 사용하여 시간 데이터 복사하고 setValues 직접 호출
        self.setValues(3, self.TIME_SYNC_ADDRESS, deepcopy(time_values))
        logger.info(f"시간 동기화 데이터 업데이트: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        gc.collect()  # 시간 업데이트 후 메모리 정리

# 서버 실행 함수
async def run_server():
    store = CustomModbusSlaveContext()
    context = ModbusServerContext(slaves=store, single=True)

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'GasCabiniet'
    identity.ModelName = 'GasCabinet Server'
    identity.MajorMinorRevision = '1.0'

    logger.info("Starting Modbus TCP GasCabinet Server...")
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