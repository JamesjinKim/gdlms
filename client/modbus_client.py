from pymodbus.client import AsyncModbusTcpClient
import asyncio
import logging
import random
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.DEBUG
)

async def generate_random_alarm():
    """랜덤 알람 생성"""
    try:
        # 알람 코드 범위 설정 (1-169)
        alarm_values = list(range(1, 169))
        
        # 랜덤하게 1-3개의 알람 선택
        num_alarms = random.randint(1, 3)
        selected_alarms = random.sample(alarm_values, num_alarms)
        
        # 선택된 알람 로깅
        for alarm in selected_alarms:
            logging.info(f"Generated Alarm: Code {alarm}")
            
        return selected_alarms
        
    except Exception as e:
        logging.error(f"Error generating alarms: {e}")
        return [1]  # 에러 발생 시 기본값 반환

async def run_client():
    client = AsyncModbusTcpClient(
        host='localhost',
        port=5020,
        timeout=10
    )

    try:
        while True:
            try:
                if not client.connected:
                    logging.info("Connecting to server...")
                    connected = await client.connect()
                    
                    if not connected:
                        logging.error("Failed to connect")
                        await asyncio.sleep(5)
                        continue
                    
                    logging.info("Connected successfully")

                # 랜덤 알람 생성 및 전송
                alarm_values = await generate_random_alarm()
                logging.info(f"Writing alarm values: {alarm_values}")
                
                try:
                    # write_registers 사용하여 알람 코드 전송
                    write_result = await client.write_registers(0, alarm_values)
                    if write_result and write_result.isError():
                        logging.error(f"Write failed: {write_result}")
                        await client.close()
                        await asyncio.sleep(5)
                        continue
                    logging.info("Alarm codes written successfully")
                    
                    # 값 읽기
                    logging.info("Reading alarm values...")
                    read_result = await client.read_holding_registers(0, count=len(alarm_values))
                    if read_result and read_result.isError():
                        logging.error(f"Read failed: {read_result}")
                        await client.close()
                        await asyncio.sleep(5)
                        continue
                    
                    read_values = read_result.registers
                    logging.info(f"Read alarm values: {read_values}")

                    # Write한 값과 Read한 값 비교
                    if alarm_values == read_values:
                        logging.info("Alarm values verified successfully")
                    else:
                        logging.error(f"Alarm values do not match. Written: {alarm_values}, Read: {read_values}")

                except Exception as e:
                    logging.error(f"Error in Modbus operation: {e}")
                    if client and client.connected:
                        await client.close()
                    await asyncio.sleep(5)
                    continue

                # 3초 대기 후 다음 알람 생성
                await asyncio.sleep(3)

            except asyncio.CancelledError:
                raise
            except Exception as e:
                logging.error(f"Error in client loop: {e}")
                if client and client.connected:
                    await client.close()
                await asyncio.sleep(5)

    except asyncio.CancelledError:
        logging.info("Client operation cancelled")
    finally:
        if client and client.connected:
            await client.close()
        logging.info("Connection closed")

if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        logging.info("Client stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")