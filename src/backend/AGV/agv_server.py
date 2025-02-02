# server.py
import asyncio
from protocol import Protocol, ProtocolConstants
import time

class ServerState:
    """서버의 현재 상태를 관리하는 클래스"""
    def __init__(self):
        self.current_state = "INIT"
        self.job_completed = False
        self.position_received = False
        self.cycle_count = 0  # 사이클 카운터 추가

async def handle_client(reader, writer):
    """클라이언트 연결 처리 코루틴"""
    addr = writer.get_extra_info('peername')
    print(f'AGV connected from {addr}')
    server_state = ServerState()
    
    try:
        while True:
            # 새로운 사이클 시작
            print(f"\n=== Cycle #{server_state.cycle_count + 1} Start ===")
            start_time = time.time()  # 사이클 시작 시간 기록
            
            # Stage 1: Status Check
            print("\n=== Stage 1: Status Check ===")
            check_message = Protocol.create_check_message()
            writer.write(check_message)
            await writer.drain()
            print(f'Sent status check command to AGV {addr}')
            
            data = await reader.read(100)
            if not data:
                break
            
            result = Protocol.parse_message(data)
            print(f'Received status reply: {result}')
            await asyncio.sleep(1)  # 단계 간 짧은 대기
            
            # Stage 2: Job Start
            print("\n=== Stage 2: Job Start ===")
            job_message = Protocol.create_job_start_message(
                1, ProtocolConstants.PORT_A, 
                99, ProtocolConstants.PORT_B
            )
            writer.write(job_message)
            await writer.drain()
            print(f'Sent job start command to AGV {addr}')
            
            # Job Reply와 Complete 대기
            for _ in range(2):
                data = await reader.read(100)
                if not data:
                    break
                result = Protocol.parse_message(data)
                print(f'Received job response: {result}')
            
            await asyncio.sleep(1)  # 단계 간 짧은 대기
            
            # Stage 3: Position Check
            print("\n=== Stage 3: Position Check ===")
            position_message = Protocol.create_position_request()
            writer.write(position_message)
            await writer.drain()
            print(f'Sent position check command to AGV {addr}')
            
            data = await reader.read(100)
            if not data:
                break
            
            result = Protocol.parse_message(data)
            print(f'Received position data: {result}')
            
            # 사이클 완료
            server_state.cycle_count += 1
            elapsed_time = time.time() - start_time
            
            # 10초에서 이미 경과된 시간을 뺀 만큼 대기
            remaining_time = max(10 - elapsed_time, 0)
            print(f"\n=== Cycle #{server_state.cycle_count} Complete ===")
            print(f"Waiting {remaining_time:.1f} seconds for next cycle...")
            await asyncio.sleep(remaining_time)
    
    except Exception as e:
        print(f'Error handling AGV {addr}: {e}')
    finally:
        print(f'AGV {addr} disconnected')
        writer.close()
        await writer.wait_closed()

async def run_server():
    """서버 실행 코루틴"""
    server = await asyncio.start_server(
        handle_client, '127.0.0.1', 8888)
    
    addr = server.sockets[0].getsockname()
    print(f'GDLMS Server listening on {addr}')
    
    try:
        async with server:
            await server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer shutting down...')
        server.close()
        await server.wait_closed()

if __name__ == '__main__':
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print('\nServer stopped by user')