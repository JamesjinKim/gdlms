import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import json
from datetime import datetime
import sys

class OptimizedStockerLogger:
    def __init__(self, log_dir='./log', log_name='stocker_server'):
        # 로그 디렉토리 생성
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 로거 생성
        self.logger = logging.getLogger(f"{log_name}_logger")
        self.logger.setLevel(logging.INFO)
        
        # 기존 핸들러 제거 (중복 방지)
        self.logger.handlers.clear()
        
        # 회전 파일 핸들러 (10MB마다 새 파일)
        log_file = log_dir / f"{log_name}.log"
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,  # 5개의 백업 로그 파일
            encoding='utf-8'
        )
        
        # 콘솔 핸들러 추가
        console_handler = logging.StreamHandler(sys.stdout)
        
        # 로그 포맷 설정
        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 핸들러 추가
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_device_data(self, device_data, data_type='plc'):
        """구조화된 장치 데이터 로깅"""
        try:
            # 현재 시간
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 로그 엔트리 생성
            log_entry = {
                'timestamp': current_time, 
                'data_type': data_type, 
                'device_info': {
                    'bunker_id': device_data.get('bunker_id', 'N/A'), 
                    'stocker_id': device_data.get('stocker_id', 'N/A')
                }, 
                'axis_data': device_data.get('axis_data', {}), 
                'alarm_code': device_data.get('alarm_code', 'N/A'),
                'gas_types': device_data.get('gas_types', []),
                'barcodes': device_data.get('barcodes', {}),
                'port_gas_types': device_data.get('port_gas_types', {})
            }
            
            # JSON 로깅
            self.logger.info(json.dumps(log_entry, ensure_ascii=False))
            
        except Exception as e:
            self.logger.error(f"로깅 중 오류: {e}", exc_info=True)

    def log_bit_data(self, bit_data):
        """비트 데이터 로깅"""
        try:
            # 현재 시간
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 로그 엔트리 생성
            log_entry = {
                'timestamp': current_time,
                'data_type': 'bit',
                'bit_signals': bit_data
            }
            
            # JSON 로깅
            self.logger.info(json.dumps(log_entry, ensure_ascii=False))
            
        except Exception as e:
            self.logger.error(f"비트 데이터 로깅 중 오류: {e}", exc_info=True)

    def log_error(self, error_message, error_type='general'):
        """오류 로깅"""
        try:
            # 현재 시간
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 오류 로그 엔트리 생성
            log_entry = {
                'timestamp': current_time,
                'error_type': error_type,
                'message': error_message
            }
            
            # 오류 로깅
            self.logger.error(json.dumps(log_entry, ensure_ascii=False))
            
        except Exception as e:
            print(f"로깅 오류: {e}")