from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
from pymodbus.server import StartAsyncTcpServer
import logging
import asyncio
import threading
from datetime import datetime
from .database_handler import DatabaseHandler
import os

# 전역 변수
modbus_thread = None
db_handler = None

class CustomModbusSlaveContext(ModbusSlaveContext):
    def __init__(self, *args, **kwargs):
        # socketio와 db_handler를 kwargs에서 추출
        self.socketio = kwargs.pop('socketio', None)
        self.db_handler = kwargs.pop('db_handler', None)
        
        # 부모 클래스 초기화
        super().__init__(*args, **kwargs)
        
        # 추가 초기화
        self.message_buffer = []
        self.buffer_size = 1000

    def setValues(self, fx, address, values):
        try:
            super().setValues(fx, address, values)
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            message_type = "Unknown"
            if fx == 3:
                message_type = "Read Holding Registers"
            elif fx == 6:
                message_type = "Write Single Register"
            elif fx == 16:
                message_type = "Write Multiple Registers"
            
            values_list = values if isinstance(values, list) else [values]
            chunks = [values_list[i:i + 100] for i in range(0, len(values_list), 100)]
            
            for i, chunk in enumerate(chunks):
                message_data = {
                    'timestamp': current_time,
                    'type': f"{message_type} (Chunk {i+1}/{len(chunks)})",
                    'address': address + (i * 100),
                    'values': chunk,
                    'function_code': fx
                }
                
                self.message_buffer.append(message_data)
                if len(self.message_buffer) > self.buffer_size:
                    self.message_buffer.pop(0)
                
                try:
                    if self.socketio:
                        self.socketio.emit('modbus_message', message_data, namespace='/')
                    if self.db_handler:
                        self.db_handler.save_message(message_data)
                    logging.info(f"Modbus Message - Type: {message_type}, Address: {address}, Values: {chunk}")
                except Exception as e:
                    logging.error(f"Error processing message: {e}")
                
        except Exception as e:
            logging.error(f"Error in setValues: {e}")
            raise

async def run_modbus_server(socketio, db_handler):
    store = CustomModbusSlaveContext(
        hr=ModbusSequentialDataBlock(0, [0] * 10000),
        socketio=socketio,
        db_handler=db_handler
    )
    context = ModbusServerContext(slaves=store, single=True)
    
    logging.info("Starting Modbus TCP Server...")
    
    await StartAsyncTcpServer(
        context=context,
        address=("0.0.0.0", 5020)
    )

def run_async_server(socketio, db_handler):
    asyncio.run(run_modbus_server(socketio, db_handler))

def setup_modbus_server(app, socketio):
    global modbus_thread, db_handler
    
    # DB 핸들러 초기화
    DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modbus_data.db')
    db_handler = DatabaseHandler(DB_FILE)
    
    # Modbus 서버 스레드 시작
    modbus_thread = threading.Thread(
        target=run_async_server,
        args=(socketio, db_handler)
    )
    modbus_thread.daemon = True
    modbus_thread.start()
    
    logging.info("Modbus server initialized")