# client.py
import asyncio
import random
from protocol import Protocol, ProtocolConstants

class AGVSimulator:
    """AGV 시뮬레이터 클래스"""
    def __init__(self):
        self.status = ProtocolConstants.STATUS_IDLE
        self.position = {'x': 1, 'y': 1}
        
    def get_random_status(self):
        """무작위 상태 반환"""
        return random.choice([
            ProtocolConstants.STATUS_IDLE,
            ProtocolConstants.STATUS_RUN,
            ProtocolConstants.STATUS_ALARM,
            ProtocolConstants.STATUS_CHARGE
        ])
    
    def get_current_position(self):
        """현재 위치 반환"""
        return self.position

async def handle_job_process(writer, agv, from_address, from_port, to_address, to_port):
    """Job 처리 프로세스 시뮬레이션"""
    # Job Reply 전송
    reply = Protocol.create_job_reply(from_address, from_port, to_address, to_port)
    writer.write(reply)
    await writer.drain()
    print(f'Sent job reply (From: {from_address}{from_port}, To: {to_address}{to_port})')
    
    # 작업 처리 시뮬레이션
    await asyncio.sleep(2)
    
    # Job Complete 전송
    complete = Protocol.create_job_complete(from_address, from_port, to_address, to_port)
    writer.write(complete)
    await writer.drain()
    print(f'Sent job complete (From: {from_address}{from_port}, To: {to_address}{to_port})')

async def agv_client():
    """AGV 클라이언트 메인 코루틴"""
    try:
        reader, writer = await asyncio.open_connection(
            '127.0.0.1', 8888)
        
        print('AGV connected to GDLMS server')
        agv = AGVSimulator()
        
        while True:
            # 서버로부터 명령 수신
            data = await reader.read(100)
            if not data:
                break
            
            print(f'\nReceived command: {data.hex()}')
            
            try:
                result = Protocol.parse_message(data)
                command_type = result['type']
                
                if command_type == 'status_check':
                    # Status Check에 대한 응답
                    print("=== Handling Status Check ===")
                    status = agv.get_random_status()
                    reply = Protocol.create_status_reply(status)
                    writer.write(reply)
                    await writer.drain()
                    print(f'Sent status reply: {status}')
                    
                elif command_type == 'job_start':
                    # Job Start에 대한 응답
                    print("=== Handling Job Start ===")
                    # From/To 정보 추출
                    from_address = result.get('from_address', '001')
                    from_port = result.get('from_port', 'A')
                    to_address = result.get('to_address', '001')
                    to_port = result.get('to_port', 'A')
                    await handle_job_process(writer, agv, from_address, from_port, to_address, to_port)
                    
                elif command_type == 'position_request':
                    # Position Check에 대한 응답
                    print("=== Handling Position Request ===")
                    pos = agv.get_current_position()
                    pos_reply = Protocol.create_position_message(pos['x'], pos['y'])
                    writer.write(pos_reply)
                    await writer.drain()
                    print(f'Sent position reply: x={pos["x"]}, y={pos["y"]}')
            
            except ValueError as e:
                print(f'Protocol error: {e}')
            
    except ConnectionRefusedError:
        print('Failed to connect to GDLMS server')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        if 'writer' in locals():
            print('Closing connection')
            writer.close()
            await writer.wait_closed()

if __name__ == '__main__':
    try:
        asyncio.run(agv_client())
    except KeyboardInterrupt:
        print('\nAGV simulator stopped by user')