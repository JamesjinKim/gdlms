from pymodbus.client import AsyncModbusTcpClient
import random
import asyncio
import logging
import datetime

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger("GasCabinetClient")

def generate_plc_data():
    """PLC 데이터 생성 함수 - Data area (0-99) 데이터 생성"""
    data = [0] * 120  # Initialize with zeros, covering all 120 WORDs

    # Basic Information (0-6)
    data[0] = 1 #random.randint(1, 2)  # Bunker ID
    data[1] = 1 #random.randint(1, 3)  # Stocker ID
    for i in range(2, 7):  # Stocker 가스 종류
        data[i] = random.randint(1, 50)

    # Machine Code and Alarm Code (7-8)
    data[7] = random.randint(0, 255)  # SEND AND RECEIVE FOR MACHINE CODE
    data[8] = random.randint(0, 500)  # Stocker Alarm Code
    data[9] = 0  # Empty

    # Position and Torque Values (10-13)
    data[10] = random.randint(0, 100)  # X축 현재값
    data[11] = random.randint(0, 100)  # Z축 현재값
    data[12] = random.randint(0, 100)  # Cap Unit 축 보호캡 분리 Torque 설정값
    data[13] = random.randint(0, 100)  # Cap Unit 축 보호캡 체결 Torque 설정값
    data[14] = random.randint(0, 100)  # PT3 (PSI)
    data[15] = random.randint(0, 100)  # PT4 (PSI)
    data[16] = random.randint(0, 100)  # WA (A Port Weight) (kg)
    data[17] = random.randint(0, 100)  # WB (B Port Weight) (kg)

    # 히터 상태 (18-21)
    data[18] = random.randint(0, 100)  # [A] JACKET HEATER (°C)
    data[19] = random.randint(0, 100)  # [A] LINE HEATER (°C)
    data[20] = random.randint(0, 100)  # [B] JACKET HEATER (°C)
    data[21] = random.randint(0, 100)  # [B] LINE HEATER (°C)

    # Empty space (22-23)
    data[22:24] = [0, 0]

    # A Port Torque & Position 데이터 (24-26)
    data[24] = random.randint(0, 100)  # [A] CGA 체결 Torque (kgf·cm)
    data[25] = random.randint(0, 100)  # [A] CAP 체결 Torque (kgf·cm)
    data[26] = random.randint(0, 255)  # [A] 실린더 Up/Down Pos (mm)

    # B Port Torque & Position 데이터 (27-29)
    data[27] = random.randint(0, 100)  # [B] CGA 체결 Torque (kgf·cm)
    data[28] = random.randint(0, 100)  # [B] CAP 체결 Torque (kgf·cm)
    data[29] = random.randint(0, 255)  # [B] 실린더 Up/Down Pos (mm)

    # Barcode Data (30-89)
    # [A] Port Barcode Data #1~#30
    data[30:60] = [ord(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')) for _ in range(30)]
    # [B] Port Barcode Data #1~#30
    data[60:90] = [ord(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')) for _ in range(30)]

    # Gas Types (90-99)
    for i in range(90, 95):  # [A] Port 가스 종류
        data[i] = random.randint(1, 5)
    for i in range(95, 100):  # [B] Port 가스 종류
        data[i] = random.randint(1, 5)

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

    return bit_data

async def run_client():
    TIME_SYNC_ADDRESS = 900  # 시간 동기화 시작 주소
    client = None
    try:
        client = AsyncModbusTcpClient('127.0.0.1', port=5020)
        await client.connect()
        logger.info("서버 연결 성공!")

        # 연결 후 바로 서버의 시간 읽기 (주소 0번부터 6개의 레지스터 읽기)
        time_response = await client.read_holding_registers(TIME_SYNC_ADDRESS, count=6)
        if not time_response.isError():
            server_time = datetime.datetime(
                year=time_response.registers[0],   # 주소 900: 년
                month=time_response.registers[1],  # 주소 901: 월
                day=time_response.registers[2],    # 주소 902: 일
                hour=time_response.registers[3],   # 주소 903: 시
                minute=time_response.registers[4], # 주소 904: 분
                second=time_response.registers[5]  # 주소 905: 초
            )
            logger.info(f"서버 시간: {server_time}")
        else:
            logger.error("시간 동기화 데이터 읽기 실패")

        while True:
            try:
                # Generate and combine data
                plc_data = generate_plc_data()
                bit_data = generate_bit_data()

                # Combine register data and bit data
                combined_data = plc_data + bit_data
                logger.info("=== 생성된 Stocker 데이터 ===")
                logger.info(f"Bunker ID: {combined_data[0]}")
                logger.info(f"Stocker ID: {combined_data[1]}")

                # PLC data 전송 (0-99 주소)
                plc_block = plc_data[:100]  # PLC 데이터만 분리
                response = await client.write_registers(0, plc_block)

                if response.isError():
                    logger.error(f"PLC data 전송 실패")
                    continue

                # Bit data 전송 (100-117 주소)
                for i, word in enumerate(bit_data):
                    try:
                        response = await client.write_register(address=i+100, value=word)
                        if response.isError():
                            logger.error(f"Bit data 전송 실패 (주소 {i+100})")
                        else:
                            logger.info(f"Bit data 전송 성공 (주소 {i+100})")
                    except Exception as e:
                        logger.error(f"Bit data 전송 오류: {e}")

                 # 전송한 데이터 확인
                result_word = await client.read_holding_registers(address=0, count=len(plc_data))
                result_bit = await client.read_coils(address=100, count=160)

                if not result_word.isError() and not result_bit.isError():
                    logger.info("전송된 데이터:")
                    logger.info(f"Word data: {result_word.registers}")
                    for i in range(0, 160, 16):
                        word = result_bit.bits[i:i+16]
                        binary = ''.join(['1' if bit else '0' for bit in word])
                        logger.info(f"Bit data (워드 {i//16}): {binary}")
                else:
                    logger.error("데이터 읽기 오류")

                # Add delay to prevent CPU overload
                await asyncio.sleep(1)

            except asyncio.CancelledError:
                logger.info("Operation cancelled.")
                break
            except Exception as e:
                logger.error(f"Data transmission error: {e}")
                break
       

    except Exception as e:
        logger.error(f"연결 오류: {e}")
    finally:
        if client and client.connected:
            await client.close()
        logger.info("클라이언트 연결 종료 완료")

if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        #pass
        print("\n사용자가 프로그램을 중단했습니다.")
    except Exception as e:
        print(f"\n예기치 않은 오류 발생: {e}")