# common/base_alarm.py
from enum import Enum
from typing import Dict, Optional, Any

class Language(Enum):
    """사용 가능한 언어 정의"""
    KO = "ko"
    EN = "en"

class AlarmSeverity(Enum):
    """알람 심각도 레벨 정의"""
    WARNING = "warning"    # 경고
    ERROR = "error"       # 에러
    CRITICAL = "critical" # 치명적

class BaseAlarm:
    """기본 알람 클래스"""
    def __init__(self, 
                 code: int, 
                 display_number: int = 0, 
                 descriptions: Optional[Dict[str, str]] = None,
                 severity: AlarmSeverity = AlarmSeverity.ERROR):
        """
        Args:
            code: 알람 코드
            display_number: 화면에 표시될 알람 번호 (기본값: 0)
            descriptions: 각 언어별 알람 설명
            severity: 알람 심각도
        """
        self.code = code
        self.display_number = display_number
        self.descriptions = descriptions or {}
        self.severity = severity

    def get_description(self, language: Language = Language.KO) -> str:
        """지정된 언어로 알람 설명을 반환"""
        return self.descriptions.get(language.value, f"Unknown Alarm Code: {self.code}")

class AlarmCodeBase:
    """알람 코드 기본 클래스"""
    _instance = None
    _alarms: Dict[int, BaseAlarm] = {}
    
    def __new__(cls):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super(AlarmCodeBase, cls).__new__(cls)
        return cls._instance

    @classmethod
    def register_alarm(cls, 
                      code: int, 
                      display_number: int = 0, 
                      ko_desc: str = "", 
                      en_desc: str = "", 
                      severity: AlarmSeverity = AlarmSeverity.ERROR) -> None:
        """새로운 알람 코드 등록

        Args:
            code: 알람 코드
            display_number: 화면에 표시될 알람 번호
            ko_desc: 한글 설명
            en_desc: 영문 설명
            severity: 알람 심각도
        """
        descriptions = {
            Language.KO.value: ko_desc,
            Language.EN.value: en_desc
        }
        cls._alarms[code] = BaseAlarm(code, display_number, descriptions, severity)

    @classmethod
    def get_description(cls, code: int, language: Language = Language.KO) -> str:
        """알람 코드에 대한 설명을 지정된 언어로 반환"""
        alarm = cls._alarms.get(code)
        if alarm:
            return alarm.get_description(language)
        return f"Unknown Alarm Code: {code}"

    @classmethod
    def get_display_number(cls, code: int) -> int:
        """알람 코드에 대한 표시 번호 반환"""
        alarm = cls._alarms.get(code)
        if alarm:
            return alarm.display_number
        return 0

    @classmethod
    def get_severity(cls, code: int) -> Optional[AlarmSeverity]:
        """알람 코드에 대한 심각도 반환"""
        alarm = cls._alarms.get(code)
        if alarm:
            return alarm.severity
        return None

    @classmethod
    def is_valid_alarm(cls, code: int) -> bool:
        """주어진 코드가 유효한 알람 코드인지 확인"""
        return code in cls._alarms