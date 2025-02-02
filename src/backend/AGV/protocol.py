# protocol.py
class ProtocolConstants:
    # Common Constants
    STX = 0x02
    ETX = 0x03
    SEPARATOR = 0x3D  # '='
    AGV_ID = 0x31    # '1'
    
    # Commands
    CMD_STATUS_CHECK = 0x43  # 'C'
    CMD_STATUS_REPLY = 0x53  # 'S'
    CMD_JOB_START = 0x4A    # 'J'
    CMD_JOB_REPLY = 0x52    # 'R'
    CMD_JOB_COMPLETE = 0x44 # 'D'
    CMD_POSITION = 0x50     # 'P'
    
    # Status Values
    STATUS_IDLE = 0x30    # '0'
    STATUS_RUN = 0x31     # '1'
    STATUS_ALARM = 0x32   # '2'
    STATUS_CHARGE = 0x33  # '3'
    
    # Port Values
    PORT_A = 0x41  # 'A'
    PORT_B = 0x42  # 'B'

class Protocol:
    @staticmethod
    def create_check_message():
        """상태 체크 메시지 생성"""
        return bytes([
            ProtocolConstants.STX,
            ProtocolConstants.AGV_ID,
            ProtocolConstants.CMD_STATUS_CHECK,
            ProtocolConstants.SEPARATOR,
            0x31,
            ProtocolConstants.ETX
        ])

    @staticmethod
    def create_job_start_message(from_pos, from_port, to_pos, to_port):
        """작업 시작 메시지 생성"""
        return bytes([
            ProtocolConstants.STX,
            ProtocolConstants.AGV_ID,
            ProtocolConstants.CMD_JOB_START,
            ProtocolConstants.SEPARATOR
        ] + list(str(from_pos).zfill(2).encode()) +
        [from_port] +
        list(str(to_pos).zfill(2).encode()) +
        [to_port,
         ProtocolConstants.ETX
        ])

    @staticmethod
    def create_position_request():
        """위치 요청 메시지 생성"""
        return bytes([
            ProtocolConstants.STX,
            ProtocolConstants.AGV_ID,
            ProtocolConstants.CMD_POSITION,
            ProtocolConstants.SEPARATOR,
            0x31,
            ProtocolConstants.ETX
        ])

    @staticmethod
    def create_status_reply(status):
        """상태 응답 메시지 생성"""
        return bytes([
            ProtocolConstants.STX,
            ProtocolConstants.AGV_ID,
            ProtocolConstants.CMD_STATUS_REPLY,
            ProtocolConstants.SEPARATOR,
            status,
            ProtocolConstants.ETX
        ])

    @staticmethod
    def create_job_reply():
        """작업 응답 메시지 생성"""
        return bytes([
            ProtocolConstants.STX,
            ProtocolConstants.AGV_ID,
            ProtocolConstants.CMD_JOB_REPLY,
            ProtocolConstants.SEPARATOR,
            0x31,
            ProtocolConstants.ETX
        ])

    @staticmethod
    def create_job_complete():
        """작업 완료 메시지 생성"""
        return bytes([
            ProtocolConstants.STX,
            ProtocolConstants.AGV_ID,
            ProtocolConstants.CMD_JOB_COMPLETE,
            ProtocolConstants.SEPARATOR,
            0x31,
            ProtocolConstants.ETX
        ])

    @staticmethod
    def create_position_message(x, y):
        """위치 정보 메시지 생성"""
        x_bytes = str(x).zfill(2).encode()
        y_bytes = str(y).zfill(2).encode()
        return bytes([
            ProtocolConstants.STX,
            ProtocolConstants.AGV_ID,
            ProtocolConstants.CMD_POSITION,
            ProtocolConstants.SEPARATOR
        ] + list(x_bytes) + list(y_bytes) + [
            ProtocolConstants.ETX
        ])

    @staticmethod
    def parse_message(data):
        """
        메시지 파싱
        Returns: dict with 'type' and additional data
        """
        if len(data) < 6 or data[0] != ProtocolConstants.STX or data[-1] != ProtocolConstants.ETX:
            raise ValueError("Invalid message format")

        command = data[2]
        message_type = None
        additional_data = {}

        if command == ProtocolConstants.CMD_STATUS_CHECK:
            message_type = 'status_check'
            
        elif command == ProtocolConstants.CMD_STATUS_REPLY:
            message_type = 'status_reply'
            status_value = data[4]
            status_map = {
                ProtocolConstants.STATUS_IDLE: "Idle",
                ProtocolConstants.STATUS_RUN: "Run",
                ProtocolConstants.STATUS_ALARM: "Alarm",
                ProtocolConstants.STATUS_CHARGE: "Charge"
            }
            additional_data['status'] = status_map.get(status_value, "Unknown")
            
        elif command == ProtocolConstants.CMD_JOB_START:
            message_type = 'job_start'
            additional_data.update({
                'from_pos': int(data[4:6].decode()),
                'from_port': chr(data[6]),
                'to_pos': int(data[7:9].decode()),
                'to_port': chr(data[9])
            })
            
        elif command == ProtocolConstants.CMD_JOB_REPLY:
            message_type = 'job_reply'
            
        elif command == ProtocolConstants.CMD_JOB_COMPLETE:
            message_type = 'job_complete'
            
        elif command == ProtocolConstants.CMD_POSITION:
            if len(data) == 6:  # Position request
                message_type = 'position_request'
            else:  # Position reply
                message_type = 'position_reply'
                additional_data.update({
                    'x': int(data[4:6].decode()),
                    'y': int(data[6:8].decode())
                })
        
        if message_type is None:
            raise ValueError(f"Unknown command: {command}")
            
        return {'type': message_type, **additional_data}
