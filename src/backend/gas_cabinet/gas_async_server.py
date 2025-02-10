import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification
from logging.handlers import TimedRotatingFileHandler
import logging
import asyncio, time, datetime
import os
from copy import deepcopy
import gc
from common.db_manager import DBManager
from gas_cabinet_alarm_code import gas_cabinet_alarm_code
from common.logger import setup_logger

# 로거 설정
logger = setup_logger('gas_cabinet_server', 'gas_cabinet_server.log')

class CustomModbusSequentialDataBlock(ModbusSequentialDataBlock):
    def __init__(self, address, values):
        super().__init__(address, values)
        # 로거 설정 추가
        self.logger = logging.getLogger('gas_cabinet_server')
        self.last_log_time = 0
        self.LOG_INTERVAL = 1
        self._buffer = []
        # DBManager 초기화 (gas_cabinet 타입으로)
        self.db_manager = DBManager('gas_cabinet')
        # 배치 저장 프로세스 시작
        self.db_manager.start_batch_save()  # 이 부분 추가
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
                    'machine_code':values[7],
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
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # PLC 데이터 영역
        values = self.getValues(1, 120)  # 주소 1부터 읽기
        bunker_id = values[0]
        gas_cabinet_id = values[1]
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
                'machine_code':values[7],
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

        # DB 저장 (비동기로 처리)
        asyncio.create_task(
            self.db_manager.update_data(
                f"gas_{gas_cabinet_id}",  # device_id 형식
                status_data  # 전체 데이터 전달
            )
        )

        # 알람 코드 확인 및 저장
        alarm_code = values[8]
        if alarm_code > 0:
            description = gas_cabinet_alarm_code.get_description(alarm_code)
            
            # Unknown Alarm Code가 아닌 경우에만 저장
            if description != f"Unknown Alarm Code: {alarm_code}":
                asyncio.create_task(
                    self.db_manager.save_alarm(
                        f"gas_{gas_cabinet_id}", 
                        alarm_code, 
                        f"Gas Cabinet {gas_cabinet_id} Alarm: Code {alarm_code} - {description}"
                    )
                )

        try:
        
            if bunker_id > 0 and gas_cabinet_id > 0:
                # PLC 데이터 영역 log 작성
                self.logger.info("=========Gas Cabinet plc_data 시작 =========\n")
                values = self.getValues(1, 120)  # 주소 1부터 읽기

                # 기본 정보
                self.logger.info(f"Bunker ID: {bunker_id}")
                self.logger.info(f"Gas Cabinet ID: {gas_cabinet_id}")
                for i in range(2, 7):
                    self.logger.info(f"Gas Cabinet 가스 종류 {i-1}: {values[i]}")
                #SEND AND RECEIVE FOR MACHINE CODE
                self.logger.info(f"Machine Code: {values[7]}")
                # 시스템 상태
                self.logger.info(f"Gas Cabinet Alarm Code: {values[8]}")
                
                # 센서 데이터
                self.logger.info(f"PT1A: {values[10]} PSI")
                self.logger.info(f"PT2A: {values[11]} PSI")
                self.logger.info(f"PT1B: {values[12]} PSI")
                self.logger.info(f"PT2B: {values[13]} PSI")
                self.logger.info(f"PT3: {values[14]} PSI")
                self.logger.info(f"PT4: {values[15]} PSI")
                self.logger.info(f"WA (A Port Weight): {values[16]} kg")
                self.logger.info(f"WB (B Port Weight): {values[17]} kg")

                # 히터 상태
                self.logger.info(f"[A] JACKET HEATER: {values[18]}°C")
                self.logger.info(f"[A] LINE HEATER: {values[19]}°C")
                self.logger.info(f"[B] JACKET HEATER: {values[20]}°C")
                self.logger.info(f"[B] LINE HEATER: {values[21]}°C")

                # A Port Torque & Position 데이터
                self.logger.info(f"[A] CGA 체결 Torque: {values[24]} kgf·cm")
                self.logger.info(f"[A] CAP 체결 Torque: {values[25]} kgf·cm")
                self.logger.info(f"[A] 실린더 Up/Down Pos: {values[26]} mm")

                # B Port Torque & Position 데이터
                self.logger.info(f"[B] CGA 체결 Torque: {values[27]} kgf·cm")
                self.logger.info(f"[B] CAP 체결 Torque: {values[28]} kgf·cm")
                self.logger.info(f"[B] 실린더 Up/Down Pos: {values[29]} mm")

                # A Port Barcode 데이터
                barcode_a = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(30, 60)])
                self.logger.info(f"[A] Port Barcode: {barcode_a}")

                # B Port Barcode 데이터
                barcode_b = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(60, 90)])
                self.logger.info(f"[B] Port Barcode: {barcode_b}")

                # Gas Types
                for i in range(90, 95):
                    self.logger.info(f"[A] Port 가스 종류 {i-89}: {values[i]}")
                for i in range(95, 100):
                    self.logger.info(f"[B] Port 가스 종류 {i-94}: {values[i]}")

                # 비트 데이터 영역 데이터 용량 문제로 주석 처리
                self.logger.info("========= Gas Cabinet Bit Area Data 시작 =========")
                bit_values = self.getValues(100, 18)  # 100번 주소부터 18개 워드 읽기

                # Word 100 - 기본 신호
                signals = ["EMG Signal", "Heart Bit", "Run/Stop Signal", "Server Connected Bit",
                        "T-LAMP RED", "T-LAMP YELLOW", "T-LAMP GREEN", "Touch 수동동작中 Signal"]
                for i, name in enumerate(signals):
                    value = bool(bit_values[0] & (1 << i))
                    self.logger.info(f"{name}: {value}")

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
                    self.logger.info(f"{name}: {value}")

                # Word 115 - B Port 상태
                b_port_status = [x.replace('[A]', '[B]') for x in a_port_status]
                for i, name in enumerate(b_port_status):
                    value = bool(bit_values[15] & (1 << i))
                    self.logger.info(f"{name}: {value}")

                # Word 116 - B Port 진행상태
                b_port_progress = [x.replace('[A]', '[B]') for x in a_port_progress]
                for i, name in enumerate(b_port_progress):
                    value = bool(bit_values[16] & (1 << i))
                    self.logger.info(f"{name}: {value}")

        except Exception as e:
            self.logger.error(f"Logging error: {e}", exc_info=True)

class CustomModbusSlaveContext(ModbusSlaveContext):
    def __init__(self):
        super().__init__(
            di=CustomModbusSequentialDataBlock(0, [0]*1000),
            co=CustomModbusSequentialDataBlock(0, [0]*1000),
            hr=CustomModbusSequentialDataBlock(0, [0]*1000),
            ir=CustomModbusSequentialDataBlock(0, [0]*1000)
        )
        self.TIME_SYNC_ADDRESS = 900
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
    identity.ProductCode = 'GasCabiniet'
    identity.ModelName = 'GasCabinet Server'
    identity.MajorMinorRevision = '1.0'
    
    logger.info("Starting Modbus TCP GasCabinet Server...")
    await asyncio.gather(
        StartAsyncTcpServer(
            context=context,
            identity=identity,
            address=("127.0.0.1", 5020)
        )
    )
    
if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
