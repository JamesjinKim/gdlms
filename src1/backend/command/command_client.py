from datetime import datetime
import asyncio
import json
from pymodbus.client import AsyncModbusTcpClient

async def send_command(port: int):
    client = AsyncModbusTcpClient('127.0.0.1', port=port)
    
    try:
        connected = await client.connect()
        
        if connected:
            command_data = {
                'type': 'shutdown',
                'command': 'Shutdown all systems'
            }
            
            command_str = json.dumps(command_data)
            register_values = [ord(c) for c in command_str]
            
            response = await client.write_registers(0, register_values)
            
            if not response.isError():
                print(f"Command sent successfully to port {port}")
            
            # close 메서드를 직접 호출하지 않고 client를 None으로 설정
            client = None
        else:
            print(f"Failed to connect to port {port}")
    
    except Exception as e:
        print(f"Error on port {port}: {type(e).__name__} - {str(e)}")

async def main():
    ports = [5022, 5023]
    for port in ports:
        await send_command(port)

if __name__ == "__main__":
    asyncio.run(main())