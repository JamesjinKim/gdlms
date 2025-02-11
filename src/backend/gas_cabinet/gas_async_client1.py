from pymodbus.client import AsyncModbusTcpClient
import random
import asyncio
import logging
import signal
import sys
import traceback

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    level=logging.DEBUG  # DEBUG 레벨로 변경
)
logger = logging.getLogger('gas_cabinet_client')

def generate_plc_data():
    """PLC 데이터 생성 함수 - Data area (0-99) 데이터 생성"""
    data = []

    # Basic Information (0-6)
    data.append(1)  #(random.randint(1, 10))  # Bunker ID (0)
    data.append(1)  #(random.randint(1, 26))  # Gas Cabinet ID (1)
    data.extend([random.randint(1, 50) for _ in range(5)])  # Gas Cabinet 가스 종류 (2-6)

    # Machine Code and Alarm Code (7-8)
    data.append(random.randint(0, 255))  # SEND AND RECEIVE FOR MACHINE CODE (7)
    data.append(random.randint(0, 255))  # Gas Cabinet Alarm Code (8)
    data.append(0)  # Empty (9)

    # Pressure Sensors (10-17)
    data.append(random.randint(0, 1000))  # PT1A
    data.append(random.randint(0, 1000))  # PT2A
    data.append(random.randint(0, 1000))  # PT1B
    data.append(random.randint(0, 1000))  # PT2B
    data.append(random.randint(0, 1000))  # PT3
    data.append(random.randint(0, 1000))  # PT4
    data.append(random.randint(0, 100))   # WA (Weight A)
    data.append(random.randint(0, 100))   # WB (Weight B)

    # Heater Values (18-21)
    data.append(random.randint(0, 100))  # [A] JACKET HEATER
    data.append(random.randint(0, 100))  # [A] LINE HEATER
    data.append(random.randint(0, 100))  # [B] JACKET HEATER
    data.append(random.randint(0, 100))  # [B] LINE HEATER

    # Empty space (22-23)
    data.extend([0, 0])

    # Torque and Position Values (24-29)
    data.append(random.randint(0, 100))  # [A] CGA 체결 Torque 설정값
    data.append(random.randint(0, 100))  # [A] CAP 체결 Torque 설정값
    data.append(random.randint(0, 255))  # [A] 실린더 Up/Down Pos 현재값
    data.append(random.randint(0, 100))  # [B] CGA 체결 Torque 설정값
    data.append(random.randint(0, 100))  # [B] CAP 체결 Torque 설정값
    data.append(random.randint(0, 255))  # [B] 실린더 Up/Down Pos 현재값

    # Barcode Data (30-89)
    # [A] Port Barcode Data #1~#30
    data.extend([ord(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')) for _ in range(30)])
    #data.extend([random.randint(32, 126) for _ in range(30)])
    # [B] Port Barcode Data #1~#30
    data.extend([ord(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')) for _ in range(30)])  
    #data.extend([random.randint(32, 126) for _ in range(30)])  

    # Gas Types (90-99)
    data.extend([random.randint(1, 50) for _ in range(5)])  # [A] Port 가스 종류
    data.extend([random.randint(1, 50) for _ in range(5)])  # [B] Port 가스 종류

    return data

def generate_bit_data():
    """PLC Bit area 데이터 생성 함수 - (100-117) 워드 생성"""
    bit_data = []

    # Word 100 (Basic signals)
    word_100 = 0
    word_100 |= random.choice([0, 1]) << 0  # EMG Signal
    word_100 |= random.choice([0, 1]) << 1  # Heart Bit
    word_100 |= random.choice([0, 1]) << 2  # Run/Stop Signal
    word_100 |= random.choice([0, 1]) << 3  # Server Connected Bit
    word_100 |= random.choice([0, 1]) << 4  # T-LAMP RED
    word_100 |= random.choice([0, 1]) << 5  # T-LAMP YELLOW
    word_100 |= random.choice([0, 1]) << 6  # T-LAMP GREEN
    word_100 |= random.choice([0, 1]) << 7  # Touch 수동동작中 Signal
    bit_data.append(word_100)

    # Word 101 (Valve status)
    word_101 = 0
    for i in range(13):  # AV1A ~ AV9
        word_101 |= random.choice([0, 1]) << i
    bit_data.append(word_101)

    # Word 102 (Heater and sensor status)
    word_102 = 0
    for i in range(9):  # Various sensors and relays
        word_102 |= random.choice([0, 1]) << i
    bit_data.append(word_102)

    # Word 103 (Port requests and completions)
    word_103 = 0
    for i in range(12):  # Port insert/remove requests and completions
        word_103 |= random.choice([0, 1]) << i
    bit_data.append(word_103)

    # Word 104 (Empty)
    bit_data.append(0)

    # Word 105 (Door and cylinder status)
    word_105 = 0
    for i in range(4):  # Cylinder presence and door status
        word_105 |= random.choice([0, 1]) << i
    bit_data.append(word_105)

    # Words 106-109 (Empty)
    bit_data.extend([0] * 4)

    # Word 110 ([A] Port operation status)
    word_110 = 0
    for i in range(13):  # A Port operation flags
        word_110 |= random.choice([0, 1]) << i
    bit_data.append(word_110)

    # Word 111 ([A] Port detailed status)
    word_111 = 0
    for i in range(16):  # A Port detailed status flags
        word_111 |= random.choice([0, 1]) << i
    bit_data.append(word_111)

    # Word 112 ([A] Port additional status)
    word_112 = 0
    for i in range(3):  # A Port additional status flags
        word_112 |= random.choice([0, 1]) << i
    bit_data.append(word_112)

    # Words 113-114 (Empty)
    bit_data.extend([0] * 2)

    # Word 115 ([B] Port operation status)
    word_115 = 0
    for i in range(13):  # B Port operation flags
        word_115 |= random.choice([0, 1]) << i
    bit_data.append(word_115)

    # Word 116 ([B] Port detailed status)
    word_116 = 0
    for i in range(16):  # B Port detailed status flags
        word_116 |= random.choice([0, 1]) << i
    bit_data.append(word_116)

    # Word 117 ([B] Port additional status)
    word_117 = 0
    for i in range(3):  # B Port additional status flags
        word_117 |= random.choice([0, 1]) << i
    bit_data.append(word_117)
    print(bit_data)
    return bit_data

async def run_client():
    try:
        # 클라이언트 설정
        client = None
        should_exit = asyncio.Event()

        async def read_time_sync_data():
            """시간 동기화 데이터 읽기"""
            try:
                if client and client.connected:
                    # 주소 0-5에서 시간 데이터 읽기
                    result = await client.read_holding_registers(
                        address=0,
                        count=6,
                        slave=1
                    )
                    if result and not result.isError():
                        time_data = result.registers
                        print("\n=== 수신된 시간 동기화 데이터 ===")
                        print(f"날짜: {time_data[0]:04d}년 {time_data[1]:02d}월 {time_data[2]:02d}일")
                        print(f"시간: {time_data[3]:02d}시 {time_data[4]:02d}분 {time_data[5]:02d}초")
                        return time_data
            except Exception as e:
                print(f"시간 동기화 데이터 읽기 오류: {e}")
            return None
    
        async def connect_client():
            nonlocal client
            try:
                logger.debug("클라이언트 연결 시작")
                if client is None:
                    logger.debug("새 클라이언트 인스턴스 생성")
                    client = AsyncModbusTcpClient(
                        host='127.0.0.1',
                        port=5020,
                        timeout=10,
                        retries=3
                    )
                    logger.debug("클라이언트 인스턴스 생성됨")

                if not client.connected:
                    logger.debug("서버 연결 시도...")
                    connected = await client.connect()
                    logger.debug(f"연결 결과: {connected}")
                    if connected:
                        logger.info("서버 연결 성공!")
                        return True
                    else:
                        logger.warning("서버 연결 실패!")
                        return False
                return True
            except Exception as e:
                logger.error(f"연결 중 예외 발생: {str(e)}")
                logger.debug(f"상세 에러: {traceback.format_exc()}")
                return False

        async def send_data():
            """데이터 전송 함수"""
            if not await connect_client():
                print("서버에 연결할 수 없습니다. 재시도 중...")
                return
                    
            try:
                # 시간 동기화 데이터 읽기
                await read_time_sync_data()

                # Data area (0-99) 데이터 전송
                data = generate_plc_data()
                print("\n=== 생성된 PLC 데이터 ===")
                print(f"Bunker ID: {data[0]}")
                print(f"Cabinet ID: {data[1]}")
                print(f"Gas Type: {data[2:7]}")
                
                # 각 레지스터를 개별적으로 전송
                for i, value in enumerate(data):
                    try:
                        if client and client.connected:
                            result = await client.write_register(
                                address=i,      # 0-99 범위의 주소
                                value=value,
                                slave=1
                            )
                            if result and hasattr(result, 'isError') and result.isError():
                                print(f"데이터 전송 실패: address={i}, value={value}")
                        else:
                            print("클라이언트 연결이 끊어졌습니다.")
                            break
                    except Exception as e:
                        print(f"레지스터 쓰기 오류 - address={i}: {e}")

                # Bit area (100-117) 데이터 전송
                bit_data = generate_bit_data()
                print(f"\n=== 생성된 Bit 데이터 ===")
                print(f"Bit data length: {len(bit_data)}")
                
                # 각 비트 데이터를 개별적으로 전송
                for i, value in enumerate(bit_data):
                    try:
                        if client and client.connected:
                            result = await client.write_register(
                                address=100 + i,    # 100-117 범위의 주소
                                value=value,
                                slave=1
                            )
                            if result and hasattr(result, 'isError') and result.isError():
                                print(f"비트 데이터 전송 실패: address={100+i}, value={value}")
                        else:
                            print("클라이언트 연결이 끊어졌습니다.")
                            break
                    except Exception as e:
                        print(f"비트 레지스터 쓰기 오류 - address={100+i}: {e}")

            except Exception as e:
                print(f"데이터 전송 중 오류 발생: {e}")

        async def client_loop():
            retry_count = 0
            max_retries = 3
            
            while not should_exit.is_set() and retry_count < max_retries:
                try:
                    logger.debug(f"연결 시도 {retry_count + 1}/{max_retries}")
                    if await connect_client():
                        logger.info("클라이언트 루프 시작")
                        while not should_exit.is_set():
                            try:
                                await send_data()
                                await asyncio.sleep(5)
                            except Exception as e:
                                logger.error(f"데이터 전송 중 오류: {str(e)}")
                                break
                    else:
                        retry_count += 1
                        if retry_count < max_retries:
                            logger.info(f"5초 후 재연결 시도...")
                            await asyncio.sleep(5)
                except Exception as e:
                    logger.error(f"클라이언트 루프 오류: {str(e)}")
                    logger.debug(f"상세 에러: {traceback.format_exc()}")
                    retry_count += 1
                    if retry_count < max_retries:
                        await asyncio.sleep(5)

            if retry_count >= max_retries:
                logger.error("최대 재시도 횟수 초과")

        # Windows에서의 시그널 핸들링
        if sys.platform == 'win32':
            def win_handler(signum, frame):
                logger.info("종료 신호 수신")
                should_exit.set()
            signal.signal(signal.SIGINT, win_handler)
        
        logger.info("=== Modbus TCP 클라이언트 시작 ===")
        await client_loop()    

    except Exception as e:
        logger.error(f"실행 중 예기치 않은 오류: {str(e)}")
        logger.debug(f"상세 에러: {traceback.format_exc()}")
    finally:
        if client and hasattr(client, 'connected') and client.connected:
            logger.debug("클라이언트 종료 시도")
            try:
                await client.close()
                logger.info("클라이언트 연결 종료 완료")
            except Exception as e:
                logger.error(f"클라이언트 종료 중 오류: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        #pass
        print("\n사용자가 프로그램을 중단했습니다.")
    except Exception as e:
        print(f"\n예기치 않은 오류 발생: {e}")