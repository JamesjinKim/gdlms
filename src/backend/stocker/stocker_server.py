import sys
from pathlib import Path
import os
sys.path.append(str(Path(__file__).parent.parent.parent))  # src/backend를 Python 경로에 추가
from backend.config import LOGS_DIR

from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
import asyncio, time, datetime
from typing import Dict, Any

# backend 패키지의 모듈들을 import
from backend.common.db_manager import DBManager
from backend.common.logger import setup_logger
from stocker_alarm_descriptions import get_stocker_descriptions

# 로거 설정
logger = setup_logger('stocker_server', 'stocker_server.log')

# 로그 디렉토리 확인 코드 추가
try:
    LOGS_DIR.mkdir(exist_ok=True, parents=True)
    print(f"Log directory created/exists at: {LOGS_DIR}")
    print(f"Log directory is writable: {os.access(LOGS_DIR, os.W_OK)}")
except Exception as e:
    print(f"Error creating log directory: {e}")

class CustomModbusSequentialDataBlock(ModbusSequentialDataBlock):
    def __init__(self, address, values):
        super().__init__(address, values)

        # 전역 로거 사용
        global logger
        self.logger = logger
        
        self.last_log_time = 0
        self.LOG_INTERVAL = 1
        self._buffer = []
        # DBManager 초기화 (stocker 타입으로)
        self.db_manager = DBManager('stocker')
        # DB에 저장할 데이터 큐 추가
        self._data_queue = []
        self._alarm_queue = []
        
        # 배치 저장 시작
        self.db_manager.start_batch_save()

    def setValues(self, address, values):
        self._buffer.append((address, values))
        super().setValues(address, values)

        current_time = time.time()
        if current_time - self.last_log_time >= self.LOG_INTERVAL:
            if self._buffer:
                self.last_log_time = current_time
                self.log_all_data()
                self._buffer.clear()

    def validate_plc_data(self, values: list) -> bool:
        """PLC 데이터 유효성 검사"""
        try:
            # 기본 길이 확인
            if len(values) < 120:  #max(word_dict.keys()):  # client의 word_dict 최대 키값 기준
                self.logger.error(f"Invalid PLC data length: {len(values)}")
                return False

            # bunker_id와 stocker_id 검증
            if not (0 < values[0] <= 10 and 0 < values[1] <= 10):
                self.logger.error(f"Invalid bunker_id or stocker_id: {values[0]}, {values[1]}")
                return False

            # gas_types 범위 검증 (2-6 인덱스)
            if not all(0 <= values[i] <= 100 for i in range(2, 7)):
                self.logger.error("Invalid gas type values")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Data validation error: {str(e)}")
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
                'gas_types': values[2:7],       # Gas Stocker 가스 종류 values[2:7].copy()
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
                '100': {  # Word 100
                    'EMG Signal': bool(bit_values[0] & (1 << 0)),
                    'Heart Bit': bool(bit_values[0] & (1 << 1)),
                    'Run/Stop Signal': bool(bit_values[0] & (1 << 2)),
                    'Server Connected Bit': bool(bit_values[0] & (1 << 3)),
                    'T-LAMP RED': bool(bit_values[0] & (1 << 4)),
                    'T-LAMP YELLOW': bool(bit_values[0] & (1 << 5)),
                    'T-LAMP GREEN': bool(bit_values[0] & (1 << 6)),
                    'Touch 수동동작中 Signal': bool(bit_values[0] & (1 << 7))
                },
                '103': {  # Word 103
                    '[A] Port 실린더 유무': bool(bit_values[3] & (1 << 0)),
                    '[B] Port 실린더 유무': bool(bit_values[3] & (1 << 1)),
                    '[A] Worker Door Open': bool(bit_values[3] & (1 << 2)),
                    '[A] Worker Door Close': bool(bit_values[3] & (1 << 3)),
                    '[A] Bunker Door Open': bool(bit_values[3] & (1 << 4)),
                    '[A] Bunker Door Close': bool(bit_values[3] & (1 << 5)),
                    '[B] Worker Door Open': bool(bit_values[3] & (1 << 6)),
                    '[B] Worker Door Close': bool(bit_values[3] & (1 << 7)),
                    '[B] Bunker Door Open': bool(bit_values[3] & (1 << 8)),
                    '[B] Bunker Door Close': bool(bit_values[3] & (1 << 9)),
                    '[공통] Initialization in Progress': bool(bit_values[3] & (1 << 10)),
                    '[공통] Initialization Complete': bool(bit_values[3] & (1 << 11))
                },
                '106': {  # Word 106
                    '[A] Cap Open Check State': bool(bit_values[6] & (1 << 0)),
                    '[A] Cap Open Check State Complete': bool(bit_values[6] & (1 << 1)),
                    '[A] Cap Open Axis Z Move Safety Position': bool(bit_values[6] & (1 << 2)),
                    '[A] Cap Open Axis Z Move Safety Position Complete': bool(bit_values[6] & (1 << 3)),
                    '[A] Cap Open Axis X Move to Cylinder': bool(bit_values[6] & (1 << 4)),
                    '[A] Cap Open Axis X Move to Cylinder Complete': bool(bit_values[6] & (1 << 5)),
                    '[A] Cap Open Cylinder Alignment in Progress': bool(bit_values[6] & (1 << 6)),
                    '[A] Cap Open Cylinder Alignment in Progress Complete': bool(bit_values[6] & (1 << 7)),
                    '[A] Cap Open Axis Z Find Cap Position': bool(bit_values[6] & (1 << 8)),
                    '[A] Cap Open Axis Z Find Cap Position Complete': bool(bit_values[6] & (1 << 9)),
                    '[A] Cap Open Cap Open in Progress': bool(bit_values[6] & (1 << 10)),
                    '[A] Cap Open Cap Open Complete': bool(bit_values[6] & (1 << 11)),
                    '[A] Cap Open Axis Z Move Safety Position-2': bool(bit_values[6] & (1 << 12)),
                    '[A] Cap Open Axis Z Move Safety Position Complete-2': bool(bit_values[6] & (1 << 13)),
                    '[A] Cap Open End': bool(bit_values[6] & (1 << 14))
                },
                '107': {  # Word 107
                    '[A] Cap Close Check State': bool(bit_values[7] & (1 << 0)),
                    '[A] Cap Close Check State Complete': bool(bit_values[7] & (1 << 1)),
                    '[A] Cap Close Axis Z Move Safety Position': bool(bit_values[7] & (1 << 2)),
                    '[A] Cap Close Axis Z Move Safety Position Complete': bool(bit_values[7] & (1 << 3)),
                    '[A] Cap Close Axis X Move to Cylinder': bool(bit_values[7] & (1 << 4)),
                    '[A] Cap Close Axis X Move to Cylinder Complete': bool(bit_values[7] & (1 << 5)),
                    '[A] Cap Close Cylinder Alignment in Progress': bool(bit_values[7] & (1 << 6)),
                    '[A] Cap Close Cylinder Alignment in Progress Complete': bool(bit_values[7] & (1 << 7)),
                    '[A] Cap Close Axiz Z Find Cylinder Neck Position': bool(bit_values[7] & (1 << 8)),
                    '[A] Cap Close Axiz Z Find Cylinder Neck Position Complete': bool(bit_values[7] & (1 << 9)),
                    '[A] Cap Close Cap Close in Progress': bool(bit_values[7] & (1 << 10)),
                    '[A] Cap Close Cap Close Complete': bool(bit_values[7] & (1 << 11)),
                    '[A] Cap Close Axis Z Move Safety Position-2': bool(bit_values[7] & (1 << 12)),
                    '[A] Cap Close Axis Z Move Safety Position Complete-2': bool(bit_values[7] & (1 << 13)),
                    '[A] Cap Close End': bool(bit_values[7] & (1 << 14))
                },
                '108': {  # Word 108
                    '[A] AGV ULD Bunker Cylinder Check': bool(bit_values[8] & (1 << 0)),
                    '[A] AGV ULD Bunker Cylinder Check Complete': bool(bit_values[8] & (1 << 1)),
                    '[A] AGV ULD Bunker Door Open Request Wait': bool(bit_values[8] & (1 << 2)),
                    '[A] AGV ULD Bunker Cap Open in Progress': bool(bit_values[8] & (1 << 3)),
                    '[A] AGV ULD Bunker Cap Open Complete': bool(bit_values[8] & (1 << 4)),
                    '[A] AGV ULD Bunker Door Open in Progress': bool(bit_values[8] & (1 << 5)),
                    '[A] AGV ULD Bunker Door Open Complete': bool(bit_values[8] & (1 << 6)),
                    '[A] AGV ULD Bunker Send Cylinder in Progress': bool(bit_values[8] & (1 << 7)),
                    '[A] AGV ULD Bunker Send Cylinder Complete': bool(bit_values[8] & (1 << 8)),
                    '[A] AGV ULD Bunker Door Close Request Wait': bool(bit_values[8] & (1 << 9)),
                    '[A] AGV ULD Bunker Door Close in Progress': bool(bit_values[8] & (1 << 10)),
                    '[A] AGV ULD Bunker Door Close Complete': bool(bit_values[8] & (1 << 11)),
                    '[A] AGV ULD Bunker End': bool(bit_values[8] & (1 << 12))
                },
                '109': {  # Word 109
                    '[A] AGV LD Bunker Cylinder Check': bool(bit_values[9] & (1 << 0)),
                    '[A] AGV LD Bunker Cylinder Check Complete': bool(bit_values[9] & (1 << 1)),
                    '[A] AGV LD Bunker Door Open Request Wait': bool(bit_values[9] & (1 << 2)),
                    '[A] AGV LD Bunker Door Open in Progress': bool(bit_values[9] & (1 << 3)),
                    '[A] AGV LD Bunker Door Open Complete': bool(bit_values[9] & (1 << 4)),
                    '[A] AGV LD Bunker Receive Cylinder in Progress': bool(bit_values[9] & (1 << 5)),
                    '[A] AGV LD Bunker Receive Cylinder Complete': bool(bit_values[9] & (1 << 6)),
                    '[A] AGV LD Bunker Door Close Request Wait': bool(bit_values[9] & (1 << 7)),
                    '[A] AGV LD Bunker Door Close in Progress': bool(bit_values[9] & (1 << 8)),
                    '[A] AGV LD Bunker Door Close Complete': bool(bit_values[9] & (1 << 9)),
                    '[A] AGV LD Bunker Cap Close in Progress': bool(bit_values[9] & (1 << 10)),
                    '[A] AGV LD Bunker Cap Close Complete': bool(bit_values[9] & (1 << 11)),
                    '[A] AGV LD Bunker End': bool(bit_values[9] & (1 << 12))
                },
                '110': {  # Word 110
                    '[A] AGV ULD Worker Cylinder Check': bool(bit_values[10] & (1 << 0)),
                    '[A] AGV ULD Worker Cylinder Check Complete': bool(bit_values[10] & (1 << 1)),
                    '[A] AGV ULD Worker Door Open Request Wait': bool(bit_values[10] & (1 << 2)),
                    '[A] AGV ULD Worker Door Open in Progress': bool(bit_values[10] & (1 << 3)),
                    '[A] AGV ULD Worker Door Open Complete': bool(bit_values[10] & (1 << 4)),
                    '[A] AGV ULD Worker Send Cylinder in Progress': bool(bit_values[10] & (1 << 5)),
                    '[A] AGV ULD Worker Send Cylinder Complete': bool(bit_values[10] & (1 << 6)),
                    '[A] AGV ULD Worker Door Close Request Wait': bool(bit_values[10] & (1 << 7)),
                    '[A] AGV ULD Worker Door Close in Progress': bool(bit_values[10] & (1 << 8)),
                    '[A] AGV ULD Worker Door Close Complete': bool(bit_values[10] & (1 << 9)),
                    '[A] AGV ULD Worker End': bool(bit_values[10] & (1 << 10))
                },
                '111': {  # Word 111
                    '[A] AGV LD Worker Cylinder Check': bool(bit_values[11] & (1 << 0)),
                    '[A] AGV LD Worker Cylinder Check Complete': bool(bit_values[11] & (1 << 1)),
                    '[A] AGV LD Worker Door Open Request Wait': bool(bit_values[11] & (1 << 2)),
                    '[A] AGV LD Worker Door Open in Progress': bool(bit_values[11] & (1 << 3)),
                    '[A] AGV LD Worker Door Open Complete': bool(bit_values[11] & (1 << 4)),
                    '[A] AGV LD Worker Receive Cylinder in Progress': bool(bit_values[11] & (1 << 5)),
                    '[A] AGV LD Worker Receive Cylinder Complete': bool(bit_values[11] & (1 << 6)),
                    '[A] AGV LD Worker Door Close Request Wait': bool(bit_values[11] & (1 << 7)),
                    '[A] AGV LD Worker Door Close in Progress': bool(bit_values[11] & (1 << 8)),
                    '[A] AGV LD Worker Door Close Complete': bool(bit_values[11] & (1 << 9)),
                    '[A] AGV LD Worker End': bool(bit_values[11] & (1 << 10))
                },
                '113': {  # Word 113
                    '[B] Cap Open Check State': bool(bit_values[13] & (1 << 0)),
                    '[B] Cap Open Check State Complete': bool(bit_values[13] & (1 << 1)),
                    '[B] Cap Open Axis Z Move Safety Position': bool(bit_values[13] & (1 << 2)),
                    '[B] Cap Open Axis Z Move Safety Position Complete': bool(bit_values[13] & (1 << 3)),
                    '[B] Cap Open Axis X Move to Cylinder': bool(bit_values[13] & (1 << 4)),
                    '[B] Cap Open Axis X Move to Cylinder Complete': bool(bit_values[13] & (1 << 5)),
                    '[B] Cap Open Cylinder Alignment in Progress': bool(bit_values[13] & (1 << 6)),
                    '[B] Cap Open Cylinder Alignment in Progress Complete': bool(bit_values[13] & (1 << 7)),
                    '[B] Cap Open Axis Z Find Cap Position': bool(bit_values[13] & (1 << 8)),
                    '[B] Cap Open Axis Z Find Cap Position Complete': bool(bit_values[13] & (1 << 9)),
                    '[B] Cap Open Cap Open in Progress': bool(bit_values[13] & (1 << 10)),
                    '[B] Cap Open Cap Open Complete': bool(bit_values[13] & (1 << 11)),
                    '[B] Cap Open Axis Z Move Safety Position-2': bool(bit_values[13] & (1 << 12)),
                    '[B] Cap Open Axis Z Move Safety Position Complete-2': bool(bit_values[13] & (1 << 13)),
                    '[B] Cap Open End': bool(bit_values[13] & (1 << 14))
                },
                '114': {  # Word 114
                    '[B] Cap Close Check State': bool(bit_values[14] & (1 << 0)),
                    '[B] Cap Close Check State Complete': bool(bit_values[14] & (1 << 1)),
                    '[B] Cap Close Axis Z Move Safety Position': bool(bit_values[14] & (1 << 2)),
                    '[B] Cap Close Axis Z Move Safety Position Complete': bool(bit_values[14] & (1 << 3)),
                    '[B] Cap Close Axis X Move to Cylinder': bool(bit_values[14] & (1 << 4)),
                    '[B] Cap Close Axis X Move to Cylinder Complete': bool(bit_values[14] & (1 << 5)),
                    '[B] Cap Close Cylinder Alignment in Progress': bool(bit_values[14] & (1 << 6)),
                    '[B] Cap Close Cylinder Alignment in Progress Complete': bool(bit_values[14] & (1 << 7)),
                    '[B] Cap Close Axiz Z Find Cylinder Neck Position': bool(bit_values[14] & (1 << 8)),
                    '[B] Cap Close Axiz Z Find Cylinder Neck Position Complete': bool(bit_values[14] & (1 << 9)),
                    '[B] Cap Close Cap Close in Progress': bool(bit_values[14] & (1 << 10)),
                    '[B] Cap Close Cap Close Complete': bool(bit_values[14] & (1 << 11)),
                    '[B] Cap Close Axis Z Move Safety Position-2': bool(bit_values[14] & (1 << 12)),
                    '[B] Cap Close Axis Z Move Safety Position Complete-2': bool(bit_values[14] & (1 << 13)),
                    '[B] Cap Close End': bool(bit_values[14] & (1 << 14))
                },
                '115': {  # Word 115
                    '[B] AGV ULD Bunker Cylinder Check': bool(bit_values[15] & (1 << 0)),
                    '[B] AGV ULD Bunker Cylinder Check Complete': bool(bit_values[15] & (1 << 1)),
                    '[B] AGV ULD Bunker Door Open Request Wait': bool(bit_values[15] & (1 << 2)),
                    '[B] AGV ULD Bunker Cap Open in Progress': bool(bit_values[15] & (1 << 3)),
                    '[B] AGV ULD Bunker Cap Open Complete': bool(bit_values[15] & (1 << 4)),
                    '[B] AGV ULD Bunker Door Open in Progress': bool(bit_values[15] & (1 << 5)),
                    '[B] AGV ULD Bunker Door Open Complete': bool(bit_values[15] & (1 << 6)),
                    '[B] AGV ULD Bunker Send Cylinder in Progress': bool(bit_values[15] & (1 << 7)),
                    '[B] AGV ULD Bunker Send Cylinder Complete': bool(bit_values[15] & (1 << 8)),
                    '[B] AGV ULD Bunker Door Close Request Wait': bool(bit_values[15] & (1 << 9)),
                    '[B] AGV ULD Bunker Door Close in Progress': bool(bit_values[15] & (1 << 10)),
                    '[B] AGV ULD Bunker Door Close Complete': bool(bit_values[15] & (1 << 11)),
                    '[B] AGV ULD Bunker End': bool(bit_values[15] & (1 << 12))
                },
                '116': {  # Word 116
                    '[B] AGV LD Bunker Cylinder Check': bool(bit_values[16] & (1 << 0)),
                    '[B] AGV LD Bunker Cylinder Check Complete': bool(bit_values[16] & (1 << 1)),
                    '[B] AGV LD Bunker Door Open Request Wait': bool(bit_values[16] & (1 << 2)),
                    '[B] AGV LD Bunker Door Open in Progress': bool(bit_values[16] & (1 << 3)),
                    '[B] AGV LD Bunker Door Open Complete': bool(bit_values[16] & (1 << 4)),
                    '[B] AGV LD Bunker Receive Cylinder in Progress': bool(bit_values[16] & (1 << 5)),
                    '[B] AGV LD Bunker Receive Cylinder Complete': bool(bit_values[16] & (1 << 6)),
                    '[B] AGV LD Bunker Door Close Request Wait': bool(bit_values[16] & (1 << 7)),
                    '[B] AGV LD Bunker Door Close in Progress': bool(bit_values[16] & (1 << 8)),
                    '[B] AGV LD Bunker Door Close Complete': bool(bit_values[16] & (1 << 9)),
                    '[B] AGV LD Bunker Cap Close in Progress': bool(bit_values[16] & (1 << 10)),
                    '[B] AGV LD Bunker Cap Close Complete': bool(bit_values[16] & (1 << 11)),
                    '[B] AGV LD Bunker End': bool(bit_values[16] & (1 << 12))
                },
                '117': {  # Word 117
                    '[B] AGV ULD Worker Cylinder Check': bool(bit_values[17] & (1 << 0)),
                    '[B] AGV ULD Worker Cylinder Check Complete': bool(bit_values[17] & (1 << 1)),
                    '[B] AGV ULD Worker Door Open Request Wait': bool(bit_values[17] & (1 << 2)),
                    '[B] AGV ULD Worker Door Open in Progress': bool(bit_values[17] & (1 << 3)),
                    '[B] AGV ULD Worker Door Open Complete': bool(bit_values[17] & (1 << 4)),
                    '[B] AGV ULD Worker Send Cylinder in Progress': bool(bit_values[17] & (1 << 5)),
                    '[B] AGV ULD Worker Send Cylinder Complete': bool(bit_values[17] & (1 << 6)),
                    '[B] AGV ULD Worker Door Close Request Wait': bool(bit_values[17] & (1 << 7)),
                    '[B] AGV ULD Worker Door Close in Progress': bool(bit_values[17] & (1 << 8)),
                    '[B] AGV ULD Worker Door Close Complete': bool(bit_values[17] & (1 << 9)),
                    '[B] AGV ULD Worker End': bool(bit_values[17] & (1 << 10))
                },
                '118': {  # Word 118
                    '[B] AGV LD Worker Cylinder Check': bool(bit_values[18] & (1 << 0)),
                    '[B] AGV LD Worker Cylinder Check Complete': bool(bit_values[18] & (1 << 1)),
                    '[B] AGV LD Worker Door Open Request Wait': bool(bit_values[18] & (1 << 2)),
                    '[B] AGV LD Worker Door Open in Progress': bool(bit_values[18] & (1 << 3)),
                    '[B] AGV LD Worker Door Open Complete': bool(bit_values[18] & (1 << 4)),
                    '[B] AGV LD Worker Receive Cylinder in Progress': bool(bit_values[18] & (1 << 5)),
                    '[B] AGV LD Worker Receive Cylinder Complete': bool(bit_values[18] & (1 << 6)),
                    '[B] AGV LD Worker Door Close Request Wait': bool(bit_values[18] & (1 << 7)),
                    '[B] AGV LD Worker Door Close in Progress': bool(bit_values[18] & (1 << 8)),
                    '[B] AGV LD Worker Door Close Complete': bool(bit_values[18] & (1 << 9)),
                    '[B] AGV LD Worker End': bool(bit_values[18] & (1 << 10))
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
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 데이터 읽기
        values = self.getValues(1, 120)
        bunker_id = values[0]
        stocker_id = values[1]

        # 유효성 검사: bunker_id와 stocker_id 확인
        if bunker_id <= 0 or stocker_id <= 0:
            return  # 조기 종료

        try:
            # PLC 데이터 영역
            self.logger.info("=========Stocker plc_data 시작 =========")
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
            bit_values = self.getValues(100, 19)

            # 장비 데이터 포맷팅
            equipment_data = self.format_equipment_data(values, 
                                                    self.getValues(100, 19), 
                                                    current_time)

            try:
                # bunker_id와 stocker_id가 모두 0보다 큰 경우에만 DB 저장
                if plc_data['bunker_id'] > 0 and plc_data['stocker_id'] > 0:
                    # DB 저장 (비동기로 처리)
                    asyncio.create_task(
                        self.db_manager.update_data(
                            f"stocker_{equipment_data['plc_data']['stocker_id']}",
                            equipment_data  # 전체 데이터 전달
                        )
                    )
                
            except Exception as e:
                self.logger.error(f"DB 저장 실패: {e}", exc_info=True)

            # 기본 정보 LOG 저장
            if values[0] > 0 and values[1] > 0:
                self.logger.info(f"Bunker ID: {values[0]}")
                self.logger.info(f"Stocker ID: {values[1]}")
                
                for i in range(2, 7):
                    self.logger.info(f"Gas Stocker 가스 종류 {i-1}: {values[i]}")

                # X, Z축 및 Torque 값
                self.logger.info(f"Stocker Alarm Code: {values[8]}")
                self.logger.info(f"X축 현재값: {values[10]}")
                self.logger.info(f"Z축 현재값: {values[11]}")
                self.logger.info(f"Cap Unit 축 보호캡 분리 Torque: {values[12]}")
                self.logger.info(f"Cap Unit 축 보호캡 체결 Torque: {values[13]}")

                # Port A Barcode
                barcode_a = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(30, 60)])
                self.logger.info(f"[A] Port Barcode: {barcode_a}")

                # Port B Barcode
                barcode_b = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(60, 90)])
                self.logger.info(f"[B] Port Barcode: {barcode_b}")

                # Port 가스 종류
                for i in range(90, 95):
                    self.logger.info(f"[A] Port 가스 종류 {i-89}: {values[i]}")
                for i in range(95, 100):
                    self.logger.info(f"[B] Port 가스 종류 {i-94}: {values[i]}")
                
                # 비트 데이터 영역. 
                self.logger.info("========= bit_data 시작 =========")
                bit_values = self.getValues(100, 19)
                
                # Word 100 - 기본 신호
                signals = ["EMG Signal", "Heart Bit", "Run/Stop Signal", "Server Connected Bit",
                            "T-LAMP RED", "T-LAMP YELLOW", "T-LAMP GREEN", "Touch 수동동작中 Signal"]
                for i, name in enumerate(signals):
                    value = bool(bit_values[0] & (1 << i))
                    self.logger.info(f"{name}: {value}")

                # Word 103 - 실린더 및 도어 상태
                cylinder_door = [
                    "[A] Port 실린더 유무", "[B] Port 실린더 유무",
                    "[A] Worker Door Open", "[A] Worker Door Close",
                    "[A] Bunker Door Open", "[A] Bunker Door Close",
                    "[B] Worker Door Open", "[B] Worker Door Close",
                    "[B] Bunker Door Open", "[B] Bunker Door Close",
                    "[공통] Initialization in Progress", "[공통] Initialization Complete"
                ]
                for i, name in enumerate(cylinder_door):
                    value = bool(bit_values[3] & (1 << i))  # 5에서 3으로 변경
                    self.logger.info(f"{name}: {value}")

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
                    self.logger.info(f"{name}: {value}")

                # Word 106-111 - A Port 관련 상태 (수정)
                a_port_status = [
                    "[A] Cap Open Check State", "[A] Cap Open Check State Complete",
                    "[A] Cap Open Axis Z Move Safety Position", 
                    "[A] Cap Open Axis Z Move Safety Position Complete",
                    "[A] Cap Open Axis X Move to Cylinder", 
                    "[A] Cap Open Axis X Move to Cylinder Complete",
                    "[A] Cap Open Cylinder Alignment in Progress", 
                    "[A] Cap Open Cylinder Alignment in Progress Complete",
                    "[A] Cap Open Axis Z Find Cap Position", 
                    "[A] Cap Open Axis Z Find Cap Position Complete",
                    "[A] Cap Open Cap Open in Progress", 
                    "[A] Cap Open Cap Open Complete",
                    "[A] Cap Open Axis Z Move Safety Position-2", 
                    "[A] Cap Open Axis Z Move Safety Position Complete-2",
                    "[A] Cap Open End"
                ]
                for i, name in enumerate(a_port_status):
                    value = bool(bit_values[6] & (1 << i))
                    self.logger.info(f"{name}: {value}")
                
                # Word 113-118 - B Port 관련 상태 (수정)
                b_port_status = [
                    "[B] Cap Open Check State", "[B] Cap Open Check State Complete",
                    "[B] Cap Open Axis Z Move Safety Position", 
                    "[B] Cap Open Axis Z Move Safety Position Complete",
                    "[B] Cap Open Axis X Move to Cylinder", 
                    "[B] Cap Open Axis X Move to Cylinder Complete",
                    "[B] Cap Open Cylinder Alignment in Progress", 
                    "[B] Cap Open Cylinder Alignment in Progress Complete",
                    "[B] Cap Open Axis Z Find Cap Position", 
                    "[B] Cap Open Axis Z Find Cap Position Complete",
                    "[B] Cap Open Cap Open in Progress", 
                    "[B] Cap Open Cap Open Complete",
                    "[B] Cap Open Axis Z Move Safety Position-2", 
                    "[B] Cap Open Axis Z Move Safety Position Complete-2",
                    "[B] Cap Open End"
                ]
                for i, name in enumerate(b_port_status):
                    value = bool(bit_values[13] & (1 << i))
                    self.logger.info(f"{name}: {value}")

                # Word 114 - B Port Cap Close 상태 (수정)
                b_port_cap_close = [
                    "[B] Cap Close Check State", "[B] Cap Close Check State Complete",
                    "[B] Cap Close Axis Z Move Safety Position", 
                    "[B] Cap Close Axis Z Move Safety Position Complete",
                    "[B] Cap Close Axis X Move to Cylinder", 
                    "[B] Cap Close Axis X Move to Cylinder Complete",
                    "[B] Cap Close Cylinder Alignment in Progress", 
                    "[B] Cap Close Cylinder Alignment in Progress Complete", 
                    "[B] Cap Close Axiz Z Find Cylinder Neck Position",
                    "[B] Cap Close Axiz Z Find Cylinder Neck Position Complete",
                    "[B] Cap Close Cap Close in Progress",
                    "[B] Cap Close Cap Close Complete",
                    "[B] Cap Close Axis Z Move Safety Position-2",
                    "[B] Cap Close Axis Z Move Safety Position Complete-2",
                    "[B] Cap Close End"
                ]
                for i, name in enumerate(b_port_cap_close):
                    value = bool(bit_values[14] & (1 << i))
                    self.logger.info(f"{name}: {value}")

                # Word 115 - B Port AGV Unload Bunker 상태
                b_port_agv_unload_bunker = [
                    "[B] AGV ULD Bunker Cylinder Check", 
                    "[B] AGV ULD Bunker Cylinder Check Complete",
                    "[B] AGV ULD Bunker Door Open Request Wait",
                    "[B] AGV ULD Bunker Cap Open in Progress", 
                    "[B] AGV ULD Bunker Cap Open Complete",
                    "[B] AGV ULD Bunker Door Open in Progress",
                    "[B] AGV ULD Bunker Door Open Complete",
                    "[B] AGV ULD Bunker Send Cylinder in Progress",
                    "[B] AGV ULD Bunker Send Cylinder Complete",
                    "[B] AGV ULD Bunker Door Close Request Wait",
                    "[B] AGV ULD Bunker Door Close in Progress",
                    "[B] AGV ULD Bunker Door Close Complete",
                    "[B] AGV ULD Bunker End"
                ]
                for i, name in enumerate(b_port_agv_unload_bunker):
                    value = bool(bit_values[15] & (1 << i))
                    self.logger.info(f"{name}: {value}")

                # Word 116 - B Port AGV Load Bunker 상태
                b_port_agv_load_bunker = [
                    "[B] AGV LD Bunker Cylinder Check",
                    "[B] AGV LD Bunker Cylinder Check Complete", 
                    "[B] AGV LD Bunker Door Open Request Wait",
                    "[B] AGV LD Bunker Door Open in Progress",
                    "[B] AGV LD Bunker Door Open Complete",
                    "[B] AGV LD Bunker Receive Cylinder in Progress",
                    "[B] AGV LD Bunker Receive Cylinder Complete",
                    "[B] AGV LD Bunker Door Close Request Wait",
                    "[B] AGV LD Bunker Door Close in Progress",
                    "[B] AGV LD Bunker Door Close Complete",
                    "[B] AGV LD Bunker Cap Close in Progress",
                    "[B] AGV LD Bunker Cap Close Complete",
                    "[B] AGV LD Bunker End"
                ]
                for i, name in enumerate(b_port_agv_load_bunker):
                    value = bool(bit_values[16] & (1 << i))
                    self.logger.info(f"{name}: {value}")

                # Word 117 - B Port AGV Unload Worker 상태
                b_port_agv_unload_worker = [
                    "[B] AGV ULD Worker Cylinder Check",
                    "[B] AGV ULD Worker Cylinder Check Complete",
                    "[B] AGV ULD Worker Door Open Request Wait",
                    "[B] AGV ULD Worker Door Open in Progress",
                    "[B] AGV ULD Worker Door Open Complete",
                    "[B] AGV ULD Worker Send Cylinder in Progress",
                    "[B] AGV ULD Worker Send Cylinder Complete",
                    "[B] AGV ULD Worker Door Close Request Wait",
                    "[B] AGV ULD Worker Door Close in Progress",
                    "[B] AGV ULD Worker Door Close Complete",
                    "[B] AGV ULD Worker End"
                ]
                for i, name in enumerate(b_port_agv_unload_worker):
                    value = bool(bit_values[17] & (1 << i))
                    self.logger.info(f"{name}: {value}")

                # Word 118 - B Port AGV Load Worker 상태
                b_port_agv_load_worker = [
                    "[B] AGV LD Worker Cylinder Check",
                    "[B] AGV LD Worker Cylinder Check Complete",
                    "[B] AGV LD Worker Door Open Request Wait",
                    "[B] AGV LD Worker Door Open in Progress",
                    "[B] AGV LD Worker Door Open Complete",
                    "[B] AGV LD Worker Receive Cylinder in Progress",
                    "[B] AGV LD Worker Receive Cylinder Complete",
                    "[B] AGV LD Worker Door Close Request Wait",
                    "[B] AGV LD Worker Door Close in Progress",
                    "[B] AGV LD Worker Door Close Complete",
                    "[B] AGV LD Worker End"
                ]
                for i, name in enumerate(b_port_agv_load_worker):
                    value = bool(bit_values[18] & (1 << i))
                    self.logger.info(f"{name}: {value}")

            # 알람 코드 확인 및 저장
            alarm_code = equipment_data['plc_data']['alarm_code']
            
            if alarm_code > 0:
                try:
                    # get_stocker_descriptions()에서 알람 정보 가져오기
                    alarm_info = get_stocker_descriptions().get(alarm_code)
                    
                    if alarm_info:
                        # 알람 정보에서 한글 설명, 영문 설명, 디스플레이 번호 추출
                        ko_desc, en_desc, display_num = alarm_info
                        
                        # Unknown Alarm Code가 아닌 경우에만 저장
                        if en_desc != f"Unknown Alarm Code: {alarm_code}":
                            asyncio.create_task(
                                self.db_manager.save_alarm(
                                    f"stocker_{equipment_data['plc_data']['stocker_id']}", 
                                    alarm_code, 
                                    f"Stocker {stocker_id} Alarm: Code {alarm_code} - {en_desc}",
                                    display_num  # 디스플레이 번호 추가
                                )
                            )
                except Exception as e:
                    logger.error(f"Alarm save failed: {e}", exc_info=True)

        except Exception as e:
            self.logger.error(f"Logging error: {e}", exc_info=True)

    def __del__(self):
        """객체 소멸 시 배치 저장 중지"""
        if hasattr(self, 'db_manager'):
            self.db_manager.stop_batch_save()

# Custom Slave Context 클래스
class CustomModbusSlaveContext(ModbusSlaveContext):
    def __init__(self):
        super().__init__(
            di=CustomModbusSequentialDataBlock(0, [0]*1000),
            co=CustomModbusSequentialDataBlock(0, [0]*1000),
            hr=CustomModbusSequentialDataBlock(0, [0]*1000),
            ir=CustomModbusSequentialDataBlock(0, [0]*1000)
        )
        # 전역 로거 사용
        global logger
        self.logger = logger
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