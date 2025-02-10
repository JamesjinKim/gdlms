import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import logging
import asyncio
from common.logger import setup_logger

# 로거 설정
logger = setup_logger('modbus_monitor', 'modbus_monitor.log')

class CustomModbusSequentialDataBlock(ModbusSequentialDataBlock):
    def __init__(self, address, values):
        super().__init__(address, values)
        self.logger = logging.getLogger('modbus_monitor')

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
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")