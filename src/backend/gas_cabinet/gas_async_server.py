import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
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
from common.db_manager import DBManager

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
                self.log_all_data()  # 동기 함수로 호출
                self._buffer.clear()
                gc.collect()
    
    async def format_data_for_db(self, values):
        """DB 저장을 위한 데이터 포맷팅"""
        try:
            # Barcode 데이터 처리
            barcode_a = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(30, 60)])
            barcode_b = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(60, 90)])
            
            # 비트 데이터 읽기
            bit_values = self.getValues(100, 18)

            # 데이터 구조화
            status_data = {
                "plc_data": {
                    "bunker_id": values[0],
                    "gas_cabinet_id": values[1],
                    "gas_types": {
                        "cabinet_gas": [values[i] for i in range(2, 7)],
                        "port_a": [values[i] for i in range(90, 95)],
                        "port_b": [values[i] for i in range(95, 100)]
                    },
                    "alarm_code": values[8],
                    "sensors": {
                        "pressure": {
                            "PT1A": values[10],
                            "PT2A": values[11],
                            "PT1B": values[12],
                            "PT2B": values[13],
                            "PT3": values[14],
                            "PT4": values[15]
                        },
                        "weight": {
                            "port_a": values[16],
                            "port_b": values[17]
                        }
                    },
                    "heaters": {
                        "port_a": {
                            "jacket": values[18],
                            "line": values[19]
                        },
                        "port_b": {
                            "jacket": values[20],
                            "line": values[21]
                        }
                    },
                    "torque_position": {
                        "port_a": {
                            "cga_torque": values[24],
                            "cap_torque": values[25],
                            "cylinder_position": values[26]
                        },
                        "port_b": {
                            "cga_torque": values[27],
                            "cap_torque": values[28],
                            "cylinder_position": values[29]
                        }
                    },
                    "barcodes": {
                        "port_a": barcode_a.strip(),
                        "port_b": barcode_b.strip()
                    }
                },
                "bit_data": {
                    "basic_signals": {  # Word 100
                        "emg_signal": bool(bit_values[0] & (1 << 0)),
                        "heart_bit": bool(bit_values[0] & (1 << 1)),
                        "run_stop": bool(bit_values[0] & (1 << 2)),
                        "server_connected": bool(bit_values[0] & (1 << 3)),
                        "t_lamp_red": bool(bit_values[0] & (1 << 4)),
                        "t_lamp_yellow": bool(bit_values[0] & (1 << 5)),
                        "t_lamp_green": bool(bit_values[0] & (1 << 6)),
                        "touch_manual": bool(bit_values[0] & (1 << 7))
                    },
                    "av_status": {  # Word 101
                        "port_a": {
                            "av1": bool(bit_values[1] & (1 << 0)),
                            "av2": bool(bit_values[1] & (1 << 1)),
                            "av3": bool(bit_values[1] & (1 << 2)),
                            "av4": bool(bit_values[1] & (1 << 3)),
                            "av5": bool(bit_values[1] & (1 << 4))
                        },
                        "port_b": {
                            "av1": bool(bit_values[1] & (1 << 5)),
                            "av2": bool(bit_values[1] & (1 << 6)),
                            "av3": bool(bit_values[1] & (1 << 7)),
                            "av4": bool(bit_values[1] & (1 << 8)),
                            "av5": bool(bit_values[1] & (1 << 9))
                        },
                        "common": {
                            "av7": bool(bit_values[1] & (1 << 10)),
                            "av8": bool(bit_values[1] & (1 << 11)),
                            "av9": bool(bit_values[1] & (1 << 12))
                        }
                    },
                    "system_status": {  # Word 102
                        "heater_relay": {
                            "port_a": {
                                "jacket": bool(bit_values[2] & (1 << 0)),
                                "line": bool(bit_values[2] & (1 << 1))
                            },
                            "port_b": {
                                "jacket": bool(bit_values[2] & (1 << 2)),
                                "line": bool(bit_values[2] & (1 << 3))
                            }
                        },
                        "safety": {
                            "gas_leak_shutdown": bool(bit_values[2] & (1 << 4)),
                            "vmb_stop_signal": bool(bit_values[2] & (1 << 5)),
                            "uv_ir_sensor": bool(bit_values[2] & (1 << 6)),
                            "high_temp_sensor": bool(bit_values[2] & (1 << 7)),
                            "smoke_sensor": bool(bit_values[2] & (1 << 8))
                        }
                    },
                    "port_operations": {  # Word 103
                        "port_a": {
                            "insert_request": bool(bit_values[3] & (1 << 0)),
                            "insert_complete": bool(bit_values[3] & (1 << 1)),
                            "remove_request": bool(bit_values[3] & (1 << 2)),
                            "remove_complete": bool(bit_values[3] & (1 << 3))
                        },
                        "port_b": {
                            "insert_request": bool(bit_values[3] & (1 << 8)),
                            "insert_complete": bool(bit_values[3] & (1 << 9)),
                            "remove_request": bool(bit_values[3] & (1 << 10)),
                            "remove_complete": bool(bit_values[3] & (1 << 11))
                        }
                    },
                    "port_status": {  # Word 105
                        "port_a": {
                            "cylinder_present": bool(bit_values[5] & (1 << 0))
                        },
                        "port_b": {
                            "cylinder_present": bool(bit_values[5] & (1 << 1))
                        },
                        "door": {
                            "open_complete": bool(bit_values[5] & (1 << 2)),
                            "close_complete": bool(bit_values[5] & (1 << 3))
                        }
                    },
                    "port_a_sequence": {  # Word 110
                        "cylinder_close": bool(bit_values[10] & (1 << 0)),
                        "first_purge_before_exchange": bool(bit_values[10] & (1 << 1)),
                        "decompression_test": bool(bit_values[10] & (1 << 2)),
                        "second_purge_before_exchange": bool(bit_values[10] & (1 << 3)),
                        "exchange_cylinder": bool(bit_values[10] & (1 << 4)),
                        "first_purge_after_exchange": bool(bit_values[10] & (1 << 5)),
                        "pressure_test": bool(bit_values[10] & (1 << 6)),
                        "second_purge_after_exchange": bool(bit_values[10] & (1 << 7)),
                        "purge_completed": bool(bit_values[10] & (1 << 8)),
                        "prepare_to_supply": bool(bit_values[10] & (1 << 9)),
                        "gas_supply_av3_choose": bool(bit_values[10] & (1 << 10)),
                        "gas_supply": bool(bit_values[10] & (1 << 11)),
                        "ready_to_supply": bool(bit_values[10] & (1 << 12))
                    },
                    "port_a_status": {  # Word 111, 112
                        "cylinder_ready": bool(bit_values[11] & (1 << 0)),
                        "cga_disconnect_complete": bool(bit_values[11] & (1 << 1)),
                        "cga_connect_complete": bool(bit_values[11] & (1 << 2)),
                        "cylinder_valve_open_complete": bool(bit_values[11] & (1 << 3)),
                        "cylinder_valve_close_complete": bool(bit_values[11] & (1 << 4)),
                        "cylinder_valve_open_status": bool(bit_values[11] & (1 << 5)),
                        "cylinder_lift_unit_ready": bool(bit_values[11] & (1 << 6)),
                        "cylinder_lift_unit_moving_up": bool(bit_values[11] & (1 << 7)),
                        "cylinder_lift_unit_moving_down": bool(bit_values[11] & (1 << 8)),
                        "cga_separation_in_progress": bool(bit_values[11] & (1 << 9)),
                        "cga_connection_in_progress": bool(bit_values[11] & (1 << 10)),
                        "cylinder_cap_separation_in_progress": bool(bit_values[11] & (1 << 11)),
                        "cylinder_valve_open_in_progress": bool(bit_values[11] & (1 << 12)),
                        "cylinder_valve_close_in_progress": bool(bit_values[11] & (1 << 13)),
                        "cylinder_alignment_in_progress": bool(bit_values[11] & (1 << 14)),
                        "cylinder_turn_in_progress": bool(bit_values[11] & (1 << 15)),
                        # Word 112
                        "cylinder_turn_complete": bool(bit_values[12] & (1 << 0)),
                        "cylinder_clamp_complete": bool(bit_values[12] & (1 << 1)),
                        "cga_connect_complete_status": bool(bit_values[12] & (1 << 2))
                    },
                    "port_b_sequence": {  # Word 115
                        "cylinder_close": bool(bit_values[15] & (1 << 0)),
                        "first_purge_before_exchange": bool(bit_values[15] & (1 << 1)),
                        "decompression_test": bool(bit_values[15] & (1 << 2)),
                        "second_purge_before_exchange": bool(bit_values[15] & (1 << 3)),
                        "exchange_cylinder": bool(bit_values[15] & (1 << 4)),
                        "first_purge_after_exchange": bool(bit_values[15] & (1 << 5)),
                        "pressure_test": bool(bit_values[15] & (1 << 6)),
                        "second_purge_after_exchange": bool(bit_values[15] & (1 << 7)),
                        "purge_completed": bool(bit_values[15] & (1 << 8)),
                        "prepare_to_supply": bool(bit_values[15] & (1 << 9)),
                        "gas_supply_av3_choose": bool(bit_values[15] & (1 << 10)),
                        "gas_supply": bool(bit_values[15] & (1 << 11)),
                        "ready_to_supply": bool(bit_values[15] & (1 << 12))
                    },
                    "port_b_status": {  # Word 116, 117
                        "cylinder_ready": bool(bit_values[16] & (1 << 0)),
                        "cga_disconnect_complete": bool(bit_values[16] & (1 << 1)),
                        "cga_connect_complete": bool(bit_values[16] & (1 << 2)),
                        "cylinder_valve_open_complete": bool(bit_values[16] & (1 << 3)),
                        "cylinder_valve_close_complete": bool(bit_values[16] & (1 << 4)),
                        "cylinder_valve_open_status": bool(bit_values[16] & (1 << 5)),
                        "cylinder_lift_unit_ready": bool(bit_values[16] & (1 << 6)),
                        "cylinder_lift_unit_moving_up": bool(bit_values[16] & (1 << 7)),
                        "cylinder_lift_unit_moving_down": bool(bit_values[16] & (1 << 8)),
                        "cga_separation_in_progress": bool(bit_values[16] & (1 << 9)),
                        "cga_connection_in_progress": bool(bit_values[16] & (1 << 10)),
                        "cylinder_cap_separation_in_progress": bool(bit_values[16] & (1 << 11)),
                        "cylinder_valve_open_in_progress": bool(bit_values[16] & (1 << 12)),
                        "cylinder_valve_close_in_progress": bool(bit_values[16] & (1 << 13)),
                        "cylinder_alignment_in_progress": bool(bit_values[16] & (1 << 14)),
                        "cylinder_turn_in_progress": bool(bit_values[16] & (1 << 15)),
                        # Word 117
                        "cylinder_turn_complete": bool(bit_values[17] & (1 << 0)),
                        "cylinder_clamp_complete": bool(bit_values[17] & (1 << 1)),
                        "cga_connect_complete_status": bool(bit_values[17] & (1 << 2))
                    }
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
            
            # 비트 데이터 영역
            bit_values = self.getValues(100, 18)  # 100번 주소부터 18개 워드 읽기
            
            # DB에 저장할 데이터 구조화
            status_data = {
                'plc_data': {
                    'bunker_id': values[0],
                    'gas_cabinet_id': values[1],
                    'gas_types': {
                        'cabinet': values[2:7],
                        'port_a': values[90:95],
                        'port_b': values[95:100]
                    },
                    'alarm_code': values[8],
                    'sensors': {
                        'pressure': {
                            'PT1A': values[10],
                            'PT2A': values[11],
                            'PT1B': values[12],
                            'PT2B': values[13],
                            'PT3': values[14],
                            'PT4': values[15]
                        },
                        'weight': {
                            'port_a': values[16],
                            'port_b': values[17]
                        }
                    },
                    'heaters': {
                        'port_a': {
                            'jacket': values[18],
                            'line': values[19]
                        },
                        'port_b': {
                            'jacket': values[20],
                            'line': values[21]
                        }
                    },
                    'torque_position': {
                        'port_a': {
                            'cga_torque': values[24],
                            'cap_torque': values[25],
                            'cylinder_position': values[26]
                        },
                        'port_b': {
                            'cga_torque': values[27],
                            'cap_torque': values[28],
                            'cylinder_position': values[29]
                        }
                    },
                    'barcodes': {
                        'port_a': ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' 
                                       for i in range(30, 60)]).strip(),
                        'port_b': ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' 
                                       for i in range(60, 90)]).strip()
                    }
                },
                'bit_data': {
                    "basic_signals": {  # Word 100
                        "emg_signal": bool(bit_values[0] & (1 << 0)),
                        "heart_bit": bool(bit_values[0] & (1 << 1)),
                        "run_stop": bool(bit_values[0] & (1 << 2)),
                        "server_connected": bool(bit_values[0] & (1 << 3)),
                        "t_lamp_red": bool(bit_values[0] & (1 << 4)),
                        "t_lamp_yellow": bool(bit_values[0] & (1 << 5)),
                        "t_lamp_green": bool(bit_values[0] & (1 << 6)),
                        "touch_manual": bool(bit_values[0] & (1 << 7))
                    },
                    "av_status": {  # Word 101
                        "port_a": {
                            "av1": bool(bit_values[1] & (1 << 0)),
                            "av2": bool(bit_values[1] & (1 << 1)),
                            "av3": bool(bit_values[1] & (1 << 2)),
                            "av4": bool(bit_values[1] & (1 << 3)),
                            "av5": bool(bit_values[1] & (1 << 4))
                        },
                        "port_b": {
                            "av1": bool(bit_values[1] & (1 << 5)),
                            "av2": bool(bit_values[1] & (1 << 6)),
                            "av3": bool(bit_values[1] & (1 << 7)),
                            "av4": bool(bit_values[1] & (1 << 8)),
                            "av5": bool(bit_values[1] & (1 << 9))
                        },
                        "common": {
                            "av7": bool(bit_values[1] & (1 << 10)),
                            "av8": bool(bit_values[1] & (1 << 11)),
                            "av9": bool(bit_values[1] & (1 << 12))
                        }
                    },
                    "system_status": {  # Word 102
                        "heater_relay": {
                            "port_a": {
                                "jacket": bool(bit_values[2] & (1 << 0)),
                                "line": bool(bit_values[2] & (1 << 1))
                            },
                            "port_b": {
                                "jacket": bool(bit_values[2] & (1 << 2)),
                                "line": bool(bit_values[2] & (1 << 3))
                            }
                        },
                        "safety": {
                            "gas_leak_shutdown": bool(bit_values[2] & (1 << 4)),
                            "vmb_stop_signal": bool(bit_values[2] & (1 << 5)),
                            "uv_ir_sensor": bool(bit_values[2] & (1 << 6)),
                            "high_temp_sensor": bool(bit_values[2] & (1 << 7)),
                            "smoke_sensor": bool(bit_values[2] & (1 << 8))
                        }
                    },
                    "port_operations": {  # Word 103
                        "port_a": {
                            "insert_request": bool(bit_values[3] & (1 << 0)),
                            "insert_complete": bool(bit_values[3] & (1 << 1)),
                            "remove_request": bool(bit_values[3] & (1 << 2)),
                            "remove_complete": bool(bit_values[3] & (1 << 3))
                        },
                        "port_b": {
                            "insert_request": bool(bit_values[3] & (1 << 8)),
                            "insert_complete": bool(bit_values[3] & (1 << 9)),
                            "remove_request": bool(bit_values[3] & (1 << 10)),
                            "remove_complete": bool(bit_values[3] & (1 << 11))
                        }
                    },
                    "port_status": {  # Word 105
                        "port_a": {
                            "cylinder_present": bool(bit_values[5] & (1 << 0))
                        },
                        "port_b": {
                            "cylinder_present": bool(bit_values[5] & (1 << 1))
                        },
                        "door": {
                            "open_complete": bool(bit_values[5] & (1 << 2)),
                            "close_complete": bool(bit_values[5] & (1 << 3))
                        }
                    },
                    "port_a_sequence": {  # Word 110
                        "cylinder_close": bool(bit_values[10] & (1 << 0)),
                        "first_purge_before_exchange": bool(bit_values[10] & (1 << 1)),
                        "decompression_test": bool(bit_values[10] & (1 << 2)),
                        "second_purge_before_exchange": bool(bit_values[10] & (1 << 3)),
                        "exchange_cylinder": bool(bit_values[10] & (1 << 4)),
                        "first_purge_after_exchange": bool(bit_values[10] & (1 << 5)),
                        "pressure_test": bool(bit_values[10] & (1 << 6)),
                        "second_purge_after_exchange": bool(bit_values[10] & (1 << 7)),
                        "purge_completed": bool(bit_values[10] & (1 << 8)),
                        "prepare_to_supply": bool(bit_values[10] & (1 << 9)),
                        "gas_supply_av3_choose": bool(bit_values[10] & (1 << 10)),
                        "gas_supply": bool(bit_values[10] & (1 << 11)),
                        "ready_to_supply": bool(bit_values[10] & (1 << 12))
                    },
                    "port_a_status": {  # Word 111, 112
                        "cylinder_ready": bool(bit_values[11] & (1 << 0)),
                        "cga_disconnect_complete": bool(bit_values[11] & (1 << 1)),
                        "cga_connect_complete": bool(bit_values[11] & (1 << 2)),
                        "cylinder_valve_open_complete": bool(bit_values[11] & (1 << 3)),
                        "cylinder_valve_close_complete": bool(bit_values[11] & (1 << 4)),
                        "cylinder_valve_open_status": bool(bit_values[11] & (1 << 5)),
                        "cylinder_lift_unit_ready": bool(bit_values[11] & (1 << 6)),
                        "cylinder_lift_unit_moving_up": bool(bit_values[11] & (1 << 7)),
                        "cylinder_lift_unit_moving_down": bool(bit_values[11] & (1 << 8)),
                        "cga_separation_in_progress": bool(bit_values[11] & (1 << 9)),
                        "cga_connection_in_progress": bool(bit_values[11] & (1 << 10)),
                        "cylinder_cap_separation_in_progress": bool(bit_values[11] & (1 << 11)),
                        "cylinder_valve_open_in_progress": bool(bit_values[11] & (1 << 12)),
                        "cylinder_valve_close_in_progress": bool(bit_values[11] & (1 << 13)),
                        "cylinder_alignment_in_progress": bool(bit_values[11] & (1 << 14)),
                        "cylinder_turn_in_progress": bool(bit_values[11] & (1 << 15)),
                        # Word 112
                        "cylinder_turn_complete": bool(bit_values[12] & (1 << 0)),
                        "cylinder_clamp_complete": bool(bit_values[12] & (1 << 1)),
                        "cga_connect_complete_status": bool(bit_values[12] & (1 << 2))
                    },
                    "port_b_sequence": {  # Word 115
                        "cylinder_close": bool(bit_values[15] & (1 << 0)),
                        "first_purge_before_exchange": bool(bit_values[15] & (1 << 1)),
                        "decompression_test": bool(bit_values[15] & (1 << 2)),
                        "second_purge_before_exchange": bool(bit_values[15] & (1 << 3)),
                        "exchange_cylinder": bool(bit_values[15] & (1 << 4)),
                        "first_purge_after_exchange": bool(bit_values[15] & (1 << 5)),
                        "pressure_test": bool(bit_values[15] & (1 << 6)),
                        "second_purge_after_exchange": bool(bit_values[15] & (1 << 7)),
                        "purge_completed": bool(bit_values[15] & (1 << 8)),
                        "prepare_to_supply": bool(bit_values[15] & (1 << 9)),
                        "gas_supply_av3_choose": bool(bit_values[15] & (1 << 10)),
                        "gas_supply": bool(bit_values[15] & (1 << 11)),
                        "ready_to_supply": bool(bit_values[15] & (1 << 12))
                    },
                    "port_b_status": {  # Word 116, 117
                        "cylinder_ready": bool(bit_values[16] & (1 << 0)),
                        "cga_disconnect_complete": bool(bit_values[16] & (1 << 1)),
                        "cga_connect_complete": bool(bit_values[16] & (1 << 2)),
                        "cylinder_valve_open_complete": bool(bit_values[16] & (1 << 3)),
                        "cylinder_valve_close_complete": bool(bit_values[16] & (1 << 4)),
                        "cylinder_valve_open_status": bool(bit_values[16] & (1 << 5)),
                        "cylinder_lift_unit_ready": bool(bit_values[16] & (1 << 6)),
                        "cylinder_lift_unit_moving_up": bool(bit_values[16] & (1 << 7)),
                        "cylinder_lift_unit_moving_down": bool(bit_values[16] & (1 << 8)),
                        "cga_separation_in_progress": bool(bit_values[16] & (1 << 9)),
                        "cga_connection_in_progress": bool(bit_values[16] & (1 << 10)),
                        "cylinder_cap_separation_in_progress": bool(bit_values[16] & (1 << 11)),
                        "cylinder_valve_open_in_progress": bool(bit_values[16] & (1 << 12)),
                        "cylinder_valve_close_in_progress": bool(bit_values[16] & (1 << 13)),
                        "cylinder_alignment_in_progress": bool(bit_values[16] & (1 << 14)),
                        "cylinder_turn_in_progress": bool(bit_values[16] & (1 << 15)),
                        # Word 117
                        "cylinder_turn_complete": bool(bit_values[17] & (1 << 0)),
                        "cylinder_clamp_complete": bool(bit_values[17] & (1 << 1)),
                        "cga_connect_complete_status": bool(bit_values[17] & (1 << 2))
                    }
                },
                'timestamp': current_time  # timestamp 필드 추가
            }

            try:
                # DB 저장 (비동기로 처리)
                asyncio.create_task(
                    self.db_manager.update_data(
                        f"gas_{values[1]}",  # Gas Cabinet ID를 사용
                        status_data  # 전체 status_data를 직접 전달
                    )
                )

                # 알람 코드 확인 및 저장
                alarm_code = values[8]
                if alarm_code > 0:
                    asyncio.create_task(
                        self.db_manager.save_alarm(
                            f"gas_{values[1]}", 
                            alarm_code, 
                            f"Gas Cabinet {values[1]} Alarm: Code {alarm_code}"
                        )
                    )
            except Exception as e:
                f.write(f"{current_time} | DB 저장 오류: {str(e)}\n")
                logger.error(f"DB 저장 실패: {e}", exc_info=True)

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