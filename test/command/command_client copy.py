from pymodbus.client import AsyncModbusTcpClient
import asyncio
import json
import logging

# 기본 로깅 설정
logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('CommandClient')

async def run_client():
    server_ports = [5022, 5023]
    
    for port in server_ports:
        try:
            logger.info(f"Connecting to port {port}")
            client = AsyncModbusTcpClient('127.0.0.1', port=port)
            connected = await client.connect()
            
            if connected:
                logger.info(f"Connected to server on port {port}")
                
                command_data = {
                    'type': 'shutdown',
                    'command': 'Shutdown all systems'
                }
                
                command_str = json.dumps(command_data)
                register_values = [ord(c) for c in command_str]
                
                response = await client.write_registers(0, register_values)
                
                if not response.isError():
                    logger.info(f"Command sent successfully to port {port}")
                
                await client.close()
            else:
                logger.error(f"Failed to connect to port {port}")
        
        except Exception as e:
            logger.error(f"Error on port {port}: {str(e)}")

async def main():
    await run_client()

if __name__ == "__main__":
    asyncio.run(main())