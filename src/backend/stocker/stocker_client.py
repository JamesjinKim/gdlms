from pymodbus.client import AsyncModbusTcpClient
from typing import Dict, List, Tuple
import random
import asyncio
import logging
import datetime

logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger("StockerClient")

def generate_plc_data() -> list:
    """Generate random data for registers."""
    data = [0] * 120  # Initialize with zeros, covering all 120 WORDs

    # Fill data with random values as per your specification
    data[0] = 1 #random.randint(1, 2)  # Bunker ID
    data[1] = 1 #random.randint(1, 3)  # Stocker ID
    for i in range(2, 7):  # Gas Stocker 가스 종류
        data[i] = random.randint(1, 5)
    data[8] = random.randint(0, 500)   # Stocker Alarm Code
    data[10] = random.randint(0, 100)  # X축 현재값
    data[11] = random.randint(0, 100)  # Z축 현재값
    data[12] = random.randint(0, 100)  # Cap Unit 축 보호캡 분리 Torque 설정값
    data[13] = random.randint(0, 100)  # Cap Unit 축 보호캡 체결 Torque 설정값

    data[30:60] = [ord(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')) for _ in range(30)]
    data[60:90] = [ord(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')) for _ in range(30)]
    
    for i in range(90, 95):  # [A] Port 가스 종류
        data[i] = random.randint(1, 5)
    for i in range(95, 100):  # [B] Port 가스 종류
        data[i] = random.randint(1, 5)

    return data

def generate_bit_data() -> List[int]:
    """
    시스템 상태 데이터를 생성하는 함수
    
    Returns:
        List[int]: 생성된 비트 데이터 리스트
    """
    # Word 주소별 비트 정의
    word_dict: Dict[int, List[Tuple[int, str]]] = {
        100: [
            (0, "EMG Signal"), 
            (1, "Heart Bit"), 
            (2, "Run/Stop Signal"),
            (3, "Server Connected Bit"), 
            (4, "T-LAMP RED"), 
            (5, "T-LAMP YELLOW"),
            (6, "T-LAMP GREEN"), 
            (7, "Touch 수동동작中 Signal")
        ],
        103: [
            (0, "[A] Port 실린더 유무"), 
            (1, "[B] Port 실린더 유무"),
            (2, "[A] Worker Door Open"), 
            (3, "[A] Worker Door Close"),
            (4, "[A] Bunker Door Open"), 
            (5, "[A] Bunker Door Close"),
            (6, "[B] Worker Door Open"), 
            (7, "[B] Worker Door Close"),
            (8, "[B] Bunker Door Open"), 
            (9, "[B] Bunker Door Close"),
            (10, "[공통] Initialization in Progress"), 
            (11, "[공통] Initialization Complete")
        ],
        106: [
            (0, "[A] Cap Open Check State"), 
            (1, "[A] Cap Open Check State Complete"),
            (2, "[A] Cap Open Axis Z Move Safety Position"), 
            (3, "[A] Cap Open Axis Z Move Safety Position Complete"),
            (4, "[A] Cap Open Axis X Move to Cylinder"), 
            (5, "[A] Cap Open Axis X Move to Cylinder Complete"),
            (6, "[A] Cap Open Cylinder Alignment in Progress"), 
            (7, "[A] Cap Open Cylinder Alignment in Progress Complete"),
            (8, "[A] Cap Open Axis Z Find Cap Position"), 
            (9, "[A] Cap Open Axis Z Find Cap Position Complete"),
            (10, "[A] Cap Open Cap Open in Progress"), 
            (11, "[A] Cap Open Cap Open Complete"),
            (12, "[A] Cap Open Axis Z Move Safety Position-2"), 
            (13, "[A] Cap Open Axis Z Move Safety Position Complete-2"),
            (14, "[A] Cap Open End")
        ],
        107: [
            (0, "[A] Cap Close Check State"), 
            (1, "[A] Cap Close Check State Complete"),
            (2, "[A] Cap Close Axis Z Move Safety Position"), 
            (3, "[A] Cap Close Axis Z Move Safety Position Complete"),
            (4, "[A] Cap Close Axis X Move to Cylinder"), 
            (5, "[A] Cap Close Axis X Move to Cylinder Complete"),
            (6, "[A] Cap Close Cylinder Alignment in Progress"), 
            (7, "[A] Cap Close Cylinder Alignment in Progress Complete"),
            (8, "[A] Cap Close Axiz Z Find Cylinder Neck Position"), 
            (9, "[A] Cap Close Axiz Z Find Cylinder Neck Position Complete"),
            (10, "[A] Cap Close Cap Close in Progress"), 
            (11, "[A] Cap Close Cap Close Complete"),
            (12, "[A] Cap Close Axis Z Move Safety Position-2"), 
            (13, "[A] Cap Close Axis Z Move Safety Position Complete-2"),
            (14, "[A] Cap Close End")
        ],
        108: [
            (0, "[A] AGV ULD Bunker Cylinder Check"), 
            (1, "[A] AGV ULD Bunker Cylinder Check Complete"),
            (2, "[A] AGV ULD Bunker Door Open Request Wait"), 
            (3, "[A] AGV ULD Bunker Cap Open in Progress"),
            (4, "[A] AGV ULD Bunker Cap Open Complete"), 
            (5, "[A] AGV ULD Bunker Door Open in Progress"),
            (6, "[A] AGV ULD Bunker Door Open Complete"), 
            (7, "[A] AGV ULD Bunker Send Cylinder in Progress"),
            (8, "[A] AGV ULD Bunker Send Cylinder Complete"), 
            (9, "[A] AGV ULD Bunker Door Close Request Wait"),
            (10, "[A] AGV ULD Bunker Door Close in Progress"), 
            (11, "[A] AGV ULD Bunker Door Close Complete"),
            (12, "[A] AGV ULD Bunker End")
        ],
        109: [
            (0, "[A] AGV LD Bunker Cylinder Check"), 
            (1, "[A] AGV LD Bunker Cylinder Check Complete"),
            (2, "[A] AGV LD Bunker Door Open Request Wait"), 
            (3, "[A] AGV LD Bunker Door Open in Progress"),
            (4, "[A] AGV LD Bunker Door Open Complete"), 
            (5, "[A] AGV LD Bunker Receive Cylinder in Progress"),
            (6, "[A] AGV LD Bunker Receive Cylinder Complete"), 
            (7, "[A] AGV LD Bunker Door Close Request Wait"),
            (8, "[A] AGV LD Bunker Door Close in Progress"), 
            (9, "[A] AGV LD Bunker Door Close Complete"),
            (10, "[A] AGV LD Bunker Cap Close in Progress"), 
            (11, "[A] AGV LD Bunker Cap Close Complete"),
            (12, "[A] AGV LD Bunker End")
        ],
        110: [
            (0, "[A] AGV ULD Worker Cylinder Check"), 
            (1, "[A] AGV ULD Worker Cylinder Check Complete"),
            (2, "[A] AGV ULD Worker Door Open Request Wait"), 
            (3, "[A] AGV ULD Worker Door Open in Progress"),
            (4, "[A] AGV ULD Worker Door Open Complete"), 
            (5, "[A] AGV ULD Worker Send Cylinder in Progress"),
            (6, "[A] AGV ULD Worker Send Cylinder Complete"), 
            (7, "[A] AGV ULD Worker Door Close Request Wait"),
            (8, "[A] AGV ULD Worker Door Close in Progress"), 
            (9, "[A] AGV ULD Worker Door Close Complete"),
            (10, "[A] AGV ULD Worker End")
        ],
        111: [
            (0, "[A] AGV LD Worker Cylinder Check"), 
            (1, "[A] AGV LD Worker Cylinder Check Complete"),
            (2, "[A] AGV LD Worker Door Open Request Wait"), 
            (3, "[A] AGV LD Worker Door Open in Progress"),
            (4, "[A] AGV LD Worker Door Open Complete"), 
            (5, "[A] AGV LD Worker Receive Cylinder in Progress"),
            (6, "[A] AGV LD Worker Receive Cylinder Complete"), 
            (7, "[A] AGV LD Worker Door Close Request Wait"),
            (8, "[A] AGV LD Worker Door Close in Progress"), 
            (9, "[A] AGV LD Worker Door Close Complete"),
            (10, "[A] AGV LD Worker End")
        ],
        113: [
            (0, "[B] Cap Open Check State"), 
            (1, "[B] Cap Open Check State Complete"),
            (2, "[B] Cap Open Axis Z Move Safety Position"), 
            (3, "[B] Cap Open Axis Z Move Safety Position Complete"),
            (4, "[B] Cap Open Axis X Move to Cylinder"), 
            (5, "[B] Cap Open Axis X Move to Cylinder Complete"),
            (6, "[B] Cap Open Cylinder Alignment in Progress"), 
            (7, "[B] Cap Open Cylinder Alignment in Progress Complete"),
            (8, "[B] Cap Open Axis Z Find Cap Position"), 
            (9, "[B] Cap Open Axis Z Find Cap Position Complete"),
            (10, "[B] Cap Open Cap Open in Progress"), 
            (11, "[B] Cap Open Cap Open Complete"),
            (12, "[B] Cap Open Axis Z Move Safety Position-2"), 
            (13, "[B] Cap Open Axis Z Move Safety Position Complete-2"),
            (14, "[B] Cap Open End")
        ],
        114: [
            (0, "[B] Cap Close Check State"), 
            (1, "[B] Cap Close Check State Complete"),
            (2, "[B] Cap Close Axis Z Move Safety Position"), 
            (3, "[B] Cap Close Axis Z Move Safety Position Complete"),
            (4, "[B] Cap Close Axis X Move to Cylinder"), 
            (5, "[B] Cap Close Axis X Move to Cylinder Complete"),
            (6, "[B] Cap Close Cylinder Alignment in Progress"), 
            (7, "[B] Cap Close Cylinder Alignment in Progress Complete"),
            (8, "[B] Cap Close Axiz Z Find Cylinder Neck Position"), 
            (9, "[B] Cap Close Axiz Z Find Cylinder Neck Position Complete"),
            (10, "[B] Cap Close Cap Close in Progress"), 
            (11, "[B] Cap Close Cap Close Complete"),
            (12, "[B] Cap Close Axis Z Move Safety Position-2"), 
            (13, "[B] Cap Close Axis Z Move Safety Position Complete-2"),
            (14, "[B] Cap Close End")
        ],
        115: [
            (0, "[B] AGV ULD Bunker Cylinder Check"), 
            (1, "[B] AGV ULD Bunker Cylinder Check Complete"),
            (2, "[B] AGV ULD Bunker Door Open Request Wait"), 
            (3, "[B] AGV ULD Bunker Cap Open in Progress"),
            (4, "[B] AGV ULD Bunker Cap Open Complete"), 
            (5, "[B] AGV ULD Bunker Door Open in Progress"),
            (6, "[B] AGV ULD Bunker Door Open Complete"), 
            (7, "[B] AGV ULD Bunker Send Cylinder in Progress"),
            (8, "[B] AGV ULD Bunker Send Cylinder Complete"), 
            (9, "[B] AGV ULD Bunker Door Close Request Wait"),
            (10, "[B] AGV ULD Bunker Door Close in Progress"), 
            (11, "[B] AGV ULD Bunker Door Close Complete"),
            (12, "[B] AGV ULD Bunker End")
        ],
        116: [
            (0, "[B] AGV LD Bunker Cylinder Check"), 
            (1, "[B] AGV LD Bunker Cylinder Check Complete"),
            (2, "[B] AGV LD Bunker Door Open Request Wait"), 
            (3, "[B] AGV LD Bunker Door Open in Progress"),
            (4, "[B] AGV LD Bunker Door Open Complete"), 
            (5, "[B] AGV LD Bunker Receive Cylinder in Progress"),
            (6, "[B] AGV LD Bunker Receive Cylinder Complete"), 
            (7, "[B] AGV LD Bunker Door Close Request Wait"),
            (8, "[B] AGV LD Bunker Door Close in Progress"), 
            (9, "[B] AGV LD Bunker Door Close Complete"),
            (10, "[B] AGV LD Bunker Cap Close in Progress"), 
            (11, "[B] AGV LD Bunker Cap Close Complete"),
            (12, "[B] AGV LD Bunker End")
        ],
        117: [
            (0, "[B] AGV ULD Worker Cylinder Check"), 
            (1, "[B] AGV ULD Worker Cylinder Check Complete"),
            (2, "[B] AGV ULD Worker Door Open Request Wait"), 
            (3, "[B] AGV ULD Worker Door Open in Progress"),
            (4, "[B] AGV ULD Worker Door Open Complete"), 
            (5, "[B] AGV ULD Worker Send Cylinder in Progress"),
            (6, "[B] AGV ULD Worker Send Cylinder Complete"), 
            (7, "[B] AGV ULD Worker Door Close Request Wait"),
            (8, "[B] AGV ULD Worker Door Close in Progress"), 
            (9, "[B] AGV ULD Worker Door Close Complete"),
            (10, "[B] AGV ULD Worker End")
        ]
    }

    try:
        # 비트 데이터 리스트 초기화
        bit_data = []
        
        # 실제 사용되는 주소 목록
        valid_addresses = sorted(word_dict.keys())
        max_address = max(valid_addresses)
        
        # 모든 주소에 대한 워드 생성 (0 ~ max_address)
        for address in range(max_address + 1):
            if address in word_dict:
                # 해당 주소에 대한 워드 생성
                word = 0
                for bit, _ in word_dict[address]:
                    # 랜덤하게 비트값 생성 (0 또는 1)
                    bit_value = random.choice([0, 1])
                    # 비트 연산으로 워드에 값 설정
                    word |= bit_value << bit
            else:
                # 미사용 주소는 0으로 설정
                word = 0
            bit_data.append(word)
            
        return bit_data

    except Exception as e:
        print(f"Error generating bit data: {str(e)}")
        return [0] * (max_address + 1)  # 에러 발생 시 모든 비트를 0으로 초기화하여 반환

async def run_client():
    client = None
    try:
        client = AsyncModbusTcpClient('127.0.0.1', port=5021)
        connected = await client.connect()
        # Improved connection attempt
        for attempt in range(3):
            try:
                connected = await client.connect()
                if connected:
                    logger.info("Server connection successful!")
                    break
                logger.warning(f"Connection attempt {attempt + 1} failed")
                await asyncio.sleep(2)  # Wait before retrying
            except Exception as conn_error:
                logger.error(f"Connection attempt {attempt + 1} error: {conn_error}")
                await asyncio.sleep(2)
        else:
            logger.error("Failed to connect after 3 attempts")
            return

        # 연결 후 바로 서버의 시간 읽기
        time_response = await client.read_holding_registers(900, count=6)
        if not time_response.isError():
            server_time = datetime.datetime(
                year=time_response.registers[0],
                month=time_response.registers[1],
                day=time_response.registers[2],
                hour=time_response.registers[3],
                minute=time_response.registers[4],
                second=time_response.registers[5]
            )
            logger.info(f"서버 시간: {server_time}")

        while True:
            try:
                #PLC 데이터
                plc_data = generate_plc_data()
                #랜덤 비트 데이터 생성
                bit_data = generate_bit_data()
                # Combine register data and bit_data
                combined_data = plc_data + bit_data
                logger.info("\n=== Generated Stocker Data ===")
                logger.info(f"Bunker ID: {combined_data[0]}")
                logger.info(f"Stocker ID: {combined_data[1]}")
                
                # PLC data 전송 (0-99 주소)
                plc_block = plc_data[:100]  # PLC 데이터만 분리
                try:
                    response = await client.write_registers(0, plc_block)
                    if response.isError():
                        logger.error(f"PLC data 전송 실패")
                    else:
                        logger.info(f"PLC data 전송 성공: {plc_data}")
                except Exception as e:
                    logger.error(f"PLC data 전송 오류: {e}")

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
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                logger.info("Operation cancelled.")
                break
            except Exception as e:
                logger.error(f"Data transmission error: {e}")
                break

    except Exception as e:
        logger.error(f"Connection error: {e}")
    finally:
        if client:
            await client.close()
            logger.info("Client connection closed.")
         
if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        logger.info("사용자가 프로그램을 중단했습니다.")
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류 발생: {e}")