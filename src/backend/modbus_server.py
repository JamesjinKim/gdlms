import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import logging
import asyncio
import asyncio
import os
from common.logger import setup_logger, LOG_CONFIG

# 로거 설정
logger = setup_logger('modbus_monitor', 'modbus_monitor.log')

class CustomModbusSequentialDataBlock(ModbusSequentialDataBlock):
    def __init__(self, address, values):
        super().__init__(address, values)
        self.logger = logging.getLogger('modbus_monitor')
         # 로그 레벨 세부 조정
        #self.logger.setLevel(logging.INFO)  # 중요한 에러만 로깅

    def setValues(self, address, values):
        try:
            # 클라이언트로부터 받은 데이터 로깅
            self.logger.info(f"Received data - Address: {address}, Values: {values}")
            
            # 실제 데이터 저장
            super().setValues(address, values)
        except Exception as e:
            self.logger.error(f"Error in setValues: {e}")

class CustomModbusSlaveContext(ModbusSlaveContext):
    def __init__(self):
        super().__init__(
            di=CustomModbusSequentialDataBlock(0, [0]*1000),
            co=CustomModbusSequentialDataBlock(0, [0]*1000),
            hr=CustomModbusSequentialDataBlock(0, [0]*1000),
            ir=CustomModbusSequentialDataBlock(0, [0]*1000)
        )

# 서버 실행 함수
async def run_server():
    # Windows에서 asyncio 이벤트 루프 정책 설정
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Context 생성
    store = CustomModbusSlaveContext()
    context = ModbusServerContext(slaves=store, single=True)

    logger.info("Starting Modbus TCP Monitor Server...")
    
    try:
        await asyncio.gather(
            StartAsyncTcpServer(
                context=context,
                address=("127.0.0.1", 5020) 
            )
        )
        # 서버가 시작될 때까지 대기
        while True:
            await asyncio.sleep(30)  # 장시간 대기
    except Exception as e:
        logger.error(f"Server start error: {e}")

def main():
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    main()