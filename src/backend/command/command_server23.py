import os
import logging
from logging.handlers import RotatingFileHandler
import asyncio
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import json
import subprocess
from datetime import datetime

# 로그 디렉토리 경로 설정
log_dir = os.path.join(os.path.dirname(__file__), 'log')

# 로그 디렉토리 생성 (존재하지 않으면)
os.makedirs(log_dir, exist_ok=True)

# 로그 파일 경로 설정
log_file = os.path.join(log_dir, 'server23_command.log')

# 로거 생성
logger = logging.getLogger("CommandServer23")
logger.setLevel(logging.INFO)

# 파일 핸들러 생성 (최대 5MB, 3개 백업)
file_handler = RotatingFileHandler(
    log_file, 
    maxBytes=5*1024*1024,  # 5MB
    backupCount=3
)
file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))

# 콘솔 핸들러 생성
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))

# 로거에 핸들러 추가
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 나머지 코드는 이전과 동일
class CustomDataBlock(ModbusSequentialDataBlock):
    def __init__(self):
        super().__init__(0, [0] * 1000)
        self.server_name = "Server23"

    def setValues(self, address, values):
        super().setValues(address, values)
        
        try:
            # 레지스터에서 문자 추출
            command_str = ''.join(chr(v) for v in values if v != 0)
            
            # JSON 파싱
            command_data = json.loads(command_str)
            logger.info(f"{self.server_name} - Received command: {command_data}")
            
            # 명령 처리 로직
            self.process_command(command_data)
        
        except json.JSONDecodeError:
            logger.error(f"{self.server_name} - Invalid JSON command")
        except Exception as e:
            logger.error(f"{self.server_name} - Command processing error: {e}")

    def process_command(self, command_data):
        """개별 서버별 특화된 명령 처리"""
        command_type = command_data.get('type', '')
        
        if command_type == 'shutdown':
            logger.warning(f"{self.server_name} - Shutdown command received!")
            # 시스템 종료 명령 (실행 환경에 맞게 수정)
            # subprocess.run(['shutdown', '/s', '/t', '0'])
        
        elif command_type == 'restart':
            logger.warning(f"{self.server_name} - Restart command received!")
            # subprocess.run(['shutdown', '/r', '/t', '0'])
        
        elif command_type == 'custom':
            # Server22만의 특별한 커스텀 명령 처리
            logger.info(f"{self.server_name} - Custom command received")

async def run_server():
    datablock = CustomDataBlock()
    store = ModbusSlaveContext(
        di=datablock, co=datablock, 
        hr=datablock, ir=datablock
    )
    context = ModbusServerContext(slaves=store, single=True)

    port = 5023  # Server23의 포트
    logger.info(f"Starting Command Server23 on port {port}")
    
    await StartAsyncTcpServer(
        context=context, 
        address=('0.0.0.0', port)
    )

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server23 stopped by user")
    except Exception as e:
        logger.error(f"Server23 error: {e}")