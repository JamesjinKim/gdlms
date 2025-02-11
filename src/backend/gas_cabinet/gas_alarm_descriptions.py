# alarms/gas_cabinet/gas_cabinet_descriptions.py
from typing import Dict, Tuple

def get_gas_cabinet_descriptions() -> Dict[int, Tuple[str, str, int]]:
    """
    Returns:
        Dict[int, Tuple[str, str, int]]: 
            key: 알람 코드
            value: (한글 설명, 영문 설명, display_number)
    """
    return {
        # Common Alarms (1-22)
        1: (
            "[공통] REDUNANCY OFF ERROR",
            "[Common] REDUNDANCY OFF ERROR",
            0
        ),
        2: (
            "[공통] EMS S/W On ERROR",
            "[Common] EMS S/W On ERROR",
            0
        ),
        3: (
            "[공통] SAFETY UNIT OUT OFF CHECK ERROR",
            "[Common] SAFETY UNIT OUT OFF CHECK ERROR",
            0
        ),
        4: (
            "[공통] SMOKE DETECT CHECK ON ERROR",
            "[Common] SMOKE DETECT CHECK ON ERROR",
            0
        ),
        5: (
            "[공통] GAS AIR PRESSURE OFF CHECK ERROR",
            "[Common] GAS AIR PRESSURE OFF CHECK ERROR",
            0
        ),
        6: (
            "[공통] AUTO AIR PRESSURE OFF CHECK ERROR",
            "[Common] AUTO AIR PRESSURE OFF CHECK ERROR",
            0
        ),
        7: (
            "[공통] DOOR OPEN CHECK OFF ERROR",
            "[Common] DOOR OPEN CHECK OFF ERROR",
            0
        ),
        8: (
            "[공통] AUTO COUPLER SYSTEM EMG STATUS ERROR",
            "[Common] AUTO COUPLER SYSTEM EMG STATUS ERROR",
            0
        ),
        9: (
            "[공통] ARS RUN OFF CHECK ERROR",
            "[Common] ARS RUN OFF CHECK ERROR",
            0
        ),
        10: (
            "[공통] UV/IR ON CHECK ERROR",
            "[Common] UV/IR ON CHECK ERROR",
            0
        ),
        11: (
            "[공통] Hi-Temp ON CHECK ERROR",
            "[Common] Hi-Temp ON CHECK ERROR",
            0
        ),
        12: (
            "[공통] Gas 2nd Leak CHECK ERROR",
            "[Common] Gas 2nd Leak CHECK ERROR",
            0
        ),
        13: (
            "[공통] Cabinet Door Open Shutdown ERROR",
            "[Common] Cabinet Door Open Shutdown ERROR",
            0
        ),
        14: (
            "[공통] Exhaust Velocity ERROR",
            "[Common] Exhaust Velocity ERROR",
            0
        ),
        15: (
            "[공통] Remote Shutdown Error",
            "[Common] Remote Shutdown Error",
            0
        ),
        16: (
            "[공통] PT1 HIGH PRESSURE STATUS Error",
            "[Common] PT1 HIGH PRESSURE STATUS Error",
            0
        ),
        20: (
            "[공통] 가스 누출 1차",
            "[Common] First gas leak Error",
            0
        ),
        21: (
            "[공통] Exhaust Fail",
            "[Common] Exhaust Fail Error",
            0
        ),
        22: (
            "[공통] VALVE LIFE TIME OVER (SOME ONE)",
            "[Common] Valve Life Time Over Error (Some One)",
            0
        ),

        # A Port Alarms (101-115)
        101: (
            "[A Port] 배관 내 잔류 가스 발생 알람",
            "[A Port] Residual Gas Generation In Pipe Error",
            0
        ),
        102: (
            "[A Port] 펄스 벤트 알람",
            "[A Port] Pulse Vent Error [Vacuum Lower Limit]",
            0
        ),
        103: (
            "[A Port] 펄스 벤트 진행 횟수 초과 알람",
            "[A Port] Pulse Vent Count Error",
            0
        ),
        104: (
            "[A Port] 배관 진공 상태 불량 알람",
            "[A Port] Pipe Vacuum Condition Error [Vacuum Lower Limit]",
            0
        ),
        105: (
            "[A Port] 배관 라인 상태 불량 알람",
            "[A Port] Pipe Line Condition Error [Vacuum Lower Limit]",
            0
        ),
        106: (
            "[A Port] 배관 질소 공급 상태 불량 알람",
            "[A Port] N2 Supply Error [Vacuum Lower Limit]",
            0
        ),
        107: (
            "[A Port] PT 감압 시험 불량 알람",
            "[A Port] PT Decompression Test Error",
            0
        ),
        108: (
            "[A Port] VT 감압 시험 불량 알람",
            "[A Port] VT Decompression Test Error",
            0
        ),
        109: (
            "[A Port] AV11 Bypass 알람",
            "[A Port] AV11 Bypass Error",
            0
        ),
        110: (
            "[A Port] AV1 Bypass 알람",
            "[A Port] AV1 Bypass Error",
            0
        ),
        111: (
            "[A Port] 가압 시험 불량 알람",
            "[A Port] Compression Test Error",
            0
        ),
        112: (
            "[A Port] 가압 시험 압력 상승 알람",
            "[A Port] Pressure Test Pressure Rise Error",
            0
        ),
        113: (
            "[A Port] 고압 가스 부족 알람",
            "[A Port] High Pressure Gas Low Error",
            0
        ),
        114: (
            "[A Port] 고압 가스 상한치 알람",
            "[A Port] High Pressure Gas Upper Limit Error",
            0
        ),
        115: (
            "[A Port] NOT STAND-BY 알람",
            "[A Port] Not Stand-By Error",
            0
        ),

        # A Port Extended Alarms (121-193)
        121: (
            "[A Port] 무게 옵셋 제로 셋팅 알람",
            "[A Port] Weight Offset Zero Setting Error",
            0
        ),
        122: (
            "[A Port] Gross 옵셋 범위 초과 알람",
            "[A Port] Gross Offset Range Over Error",
            0
        ),
        123: (
            "[A Port] NOT CHANGE 알람",
            "[A Port] Not Change Error",
            0
        ),
        131: (
            "[A Port] PT1 STAND-BY 저압 알람",
            "[A Port] PT1 STAND-BY Low Pressure Error",
            0
        ),
        133: (
            "[A Port] 공급 라인 BYPASS 발생 알람",
            "[A Port] Supply Line Bypass Occurrence Error",
            0
        ),
        140: (
            "[A Port] Manifold Heater 센서 단선 알람",
            "[A Port] Manifold Heater Sensor Open Circuit Error",
            0
        ),
        141: (
            "[A Port] Line Heater 센서 단선 알람",
            "[A Port] Line Heater Sensor Open Circuit Error",
            0
        ),
        142: (
            "[A Port] Jacket Heater 센서 단선 알람",
            "[A Port] Jacket Heater Sensor Open Circuit Error",
            0
        ),
        143: (
            "[A Port] Cooling 단선 알람",
            "[A Port] Cooling Open Circuit Error",
            0
        ),
        144: (
            "[A Port] MANIFOLD HEATER 고온 알람",
            "[A Port] Maniford Heater High Temperature Error",
            0
        ),
        145: (
            "[A Port] Line HEATER 고온 알람",
            "[A Port] Line Heater High Temperature Error",
            0
        ),
        146: (
            "[A Port] Jacket Heater 고온 알람",
            "[A Port] Jacket Heater High Temperature Error",
            0
        ),
        147: (
            "[A Port] MANIFOLD HEATER BIMETAL 알람",
            "[A Port] Manifold Heater Bimetal Error",
            0
        ),
        148: (
            "[A Port] LINE HEATER BIMETAL 알람",
            "[A Port] Line Heater Bimetal Error",
            0
        ),
        149: (
            "[A Port] Jacket HEATER BIMETAL 알람",
            "[A Port] Jacket Heater Bimetal Error",
            0
        ),
        150: (
            "[A Port] Cooling Jacket 1차 고온 알람",
            "[A Port] Cooling Jacket 1st High Temperature Error",
            0
        ),
        151: (
            "[A Port] Cooling Jacket 2차 고온",
            "[A Port] Cooling Jacket 2nd High Temperature Error",
            0
        ),

        # A Port PT Alarms (160-193)
        160: (
            "[A Port] PT1 2차 고압 상태",
            "[A Port] PT1 Secondary High Pressure Error",
            0
        ),
        161: (
            "[A Port] PT1 1차 고압 상태",
            "[A Port] PT1 Primary High Pressure Error",
            0
        ),
        162: (
            "[A Port] PT1 1차 저압 상태",
            "[A Port] PT1 Primary Low Pressure Error",
            0
        ),
        163: (
            "[A Port] PT1 2차 저압 상태",
            "[A Port] PT1 Secondary Low Pressure Error",
            0
        ),
        164: (
            "[A Port] PT2 2차 고압 상태 (Shutdown)",
            "[A Port] PT2 Secondary High Pressure Error (Shutdown)",
            0
        ),
        165: (
            "[A Port] PT2 1차 고압 상태",
            "[A Port] PT2 Primary High Pressure Error",
            0
        ),
        166: (
            "[A Port] PT2 1차 저압 상태",
            "[A Port] PT2 Primary Low Pressure Error",
            0
        ),
        167: (
            "[A Port] PT2 2차 저압 상태",
            "[A Port] PT2 Secondary Low Pressure Error",
            0
        ),
        168: (
            "[A Port] PT3 고압 상태",
            "[A Port] PT3 High Pressure Error",
            0
        ),
        169: (
            "[A Port] PT3 저압 상태",
            "[A Port] PT3 Low Pressure Error",
            0
        ),
        170: (
            "[A Port] AV1 BY-PASS 상태",
            "[A Port] AV1 BY-PASS Status Error",
            0
        ),
        180: (
            "[A Port] 무게 과 중량",
            "[A Port] Weight Over Error",
            0
        ),
        181: (
            "[A Port] 무게 이상",
            "[A Port] Weight Error",
            0
        ),
        182: (
            "[A Port] 무게 1차 저 중량 상태",
            "[A Port] Weight 1st Low Weight Error",
            0
        ),
        183: (
            "[A Port] 무게 2차 저 중량 상태",
            "[A Port] Weight 2nd Low Weight Error",
            0
        ),
        190: (
            "[A Port] PT1 음압 상한",
            "[A Port] PT1 Pressure Plus Limit Error",
            0
        ),
        191: (
            "[A Port] PT1 음압 하한",
            "[A Port] PT1 Pressure Minus Limit Error",
            0
        ),
        192: (
            "[A Port] PT2 음압 상한",
            "[A Port] PT1 Pressure Plus Limit Error",
            0
        ),
        193: (
            "[A Port] PT2 음압 하한",
            "[A Port] PT1 Pressure Minus Limit Error",
            0
        ),

        # B Port Alarms (201-215)
        201: (
            "[B Port] 배관 내 잔류 가스 발생 알람",
            "[B Port] Residual Gas Generation In Pipe Error",
            0
        ),
        202: (
            "[B Port] 펄스 벤트 알람",
            "[B Port] Pulse Vent Error [Vacuum Lower Limit]",
            0
        ),
        203: (
            "[B Port] 펄스 벤트 진행 횟수 초과 알람",
            "[B Port] Pulse Vent Count Error",
            0
        ),
        204: (
            "[B Port] 배관 진공 상태 불량 알람",
            "[B Port] Pipe Vacuum Condition Error [Vacuum Lower Limit]",
            0
        ),
        205: (
            "[B Port] 배관 라인 상태 불량 알람",
            "[B Port] Pipe Line Condition Error [Vacuum Lower Limit]",
            0
        ),
        206: (
            "[B Port] 배관 질소 공급 상태 불량 알람",
            "[B Port] N2 Supply Error [Vacuum Lower Limit]",
            0
        ),
        207: (
            "[B Port] PT 감압 시험 불량 알람",
            "[B Port] PT Decompression Test Error",
            0
        ),
        208: (
            "[B Port] VT 감압 시험 불량 알람",
            "[B Port] VT Decompression Test Error",
            0
        ),
        209: (
            "[B Port] AV11 Bypass 알람",
            "[B Port] AV11 Bypass Error",
            0
        ),
        210: (
            "[B Port] AV1 Bypass 알람",
            "[B Port] AV1 Bypass Error",
            0
        ),
        211: (
            "[B Port] 가압 시험 불량 알람",
            "[B Port] Compression Test Error",
            0
        ),
        212: (
            "[B Port] 가압 시험 압력 상승 알람",
            "[B Port] Pressure Test Pressure Rise Error",
            0
        ),
        213: (
            "[B Port] 고압 가스 부족 알람",
            "[B Port] High Pressure Gas Low Error",
            0
        ),
        214: (
            "[B Port] 고압 가스 상한치 알람",
            "[B Port] High Pressure Gas Upper Limit Error",
            0
        ),
        215: (
            "[B Port] NOT STAND-BY 알람",
            "[B Port] Not Stand-By Error",
            0
        ),

        # B Port Extended Alarms (221-293)
        221: (
            "[B Port] 무게 옵셋 제로 셋팅 알람",
            "[B Port] Weight Offset Zero Setting Error",
            0
        ),
        222: (
            "[B Port] Gross 옵셋 범위 초과 알람",
            "[B Port] Gross Offset Range Over Error",
            0
        ),
        223: (
            "[B Port] NOT CHANGE 알람",
            "[B Port] Not Change Error",
            0
        ),
        231: (
            "[B Port] PT1 STAND-BY 저압 알람",
            "[B Port] PT1 STAND-BY Low Pressure Error",
            0
        ),
        233: (
            "[B Port] 공급 라인 BYPASS 발생 알람",
            "[B Port] Supply Line Bypass Occurrence Error",
            0
        ),
        240: (
            "[B Port] Manifold Heater 센서 단선 알람",
            "[B Port] Manifold Heater Sensor Open Circuit Error",
            0
        ),
        241: (
            "[B Port] Line Heater 센서 단선 알람",
            "[B Port] Line Heater Sensor Open Circuit Error",
            0
        ),
        242: (
            "[B Port] Jacket Heater 센서 단선 알람",
            "[B Port] Jacket Heater Sensor Open Circuit Error",
            0
        ),
        243: (
            "[B Port] Cooling 단선 알람",
            "[B Port] Cooling Open Circuit Error",
            0
        ),
        244: (
            "[B Port] MANIFOLD HEATER 고온 알람",
            "[B Port] Maniford Heater High Temperature Error",
            0
        ),
        245: (
            "[B Port] Line HEATER 고온 알람",
            "[B Port] Line Heater High Temperature Error",
            0
        ),
        246: (
            "[B Port] Jacket Heater 고온 알람",
            "[B Port] Jacket Heater High Temperature Error",
            0
        ),
        247: (
            "[B Port] MANIFOLD HEATER BIMETAL 알람",
            "[B Port] Manifold Heater Bimetal Error",
            0
        ),
        248: (
            "[B Port] LINE HEATER BIMETAL 알람",
            "[B Port] Line Heater Bimetal Error",
            0
        ),
        249: (
            "[B Port] Jacket HEATER BIMETAL 알람",
            "[B Port] Jacket Heater Bimetal Error",
            0
        ),
        250: (
            "[B Port] Cooling Jacket 1차 고온 알람",
            "[B Port] Cooling Jacket 1st High Temperature Error",
            0
        ),
        251: (
            "[B Port] Cooling Jacket 2차 고온",
            "[B Port] Cooling Jacket 2nd High Temperature Error",
            0
        ),
        # B Port PT Alarms (260-293)
        260: (
            "[B Port] PT1 2차 고압 상태",
            "[B Port] PT1 Secondary High Pressure Error",
            0
        ),
        261: (
            "[B Port] PT1 1차 고압 상태",
            "[B Port] PT1 Primary High Pressure Error",
            0
        ),
        262: (
            "[B Port] PT1 1차 저압 상태",
            "[B Port] PT1 Primary Low Pressure Error",
            0
        ),
        263: (
            "[B Port] PT1 2차 저압 상태",
            "[B Port] PT1 Secondary Low Pressure Error",
            0
        ),
        264: (
            "[B Port] PT2 2차 고압 상태 (Shutdown)",
            "[B Port] PT2 Secondary High Pressure Error (Shutdown)",
            0
        ),
        265: (
            "[B Port] PT2 1차 고압 상태",
            "[B Port] PT2 Primary High Pressure Error",
            0
        ),
        266: (
            "[B Port] PT2 1차 저압 상태",
            "[B Port] PT2 Primary Low Pressure Error",
            0
        ),
        267: (
            "[B Port] PT2 2차 저압 상태",
            "[B Port] PT2 Secondary Low Pressure Error",
            0
        ),
        268: (
            "[B Port] PT3 고압 상태",
            "[B Port] PT3 High Pressure Error",
            0
        ),
        269: (
            "[B Port] PT3 저압 상태",
            "[B Port] PT3 Low Pressure Error",
            0
        ),
        270: (
            "[B Port] AV1 BY-PASS 상태",
            "[B Port] AV1 BY-PASS Status Error",
            0
        ),
        280: (
            "[B Port] 무게 과 중량",
            "[B Port] Weight Over Error",
            0
        ),
        281: (
            "[B Port] 무게 이상",
            "[B Port] Weight Error",
            0
        ),
        282: (
            "[B Port] 무게 1차 저 중량 상태",
            "[B Port] Weight 1st Low Weight Error",
            0
        ),
        283: (
            "[B Port] 무게 2차 저 중량 상태",
            "[B Port] Weight 2nd Low Weight Error",
            0
        ),
        290: (
            "[B Port] PT1 음압 상한",
            "[B Port] PT1 Pressure Plus Limit Error",
            0
        ),
        291: (
            "[B Port] PT1 음압 하한",
            "[B Port] PT1 Pressure Minus Limit Error",
            0
        ),
        292: (
            "[B Port] PT2 음압 상한",
            "[B Port] PT1 Pressure Plus Limit Error",
            0
        ),
        293: (
            "[B Port] PT2 음압 하한",
            "[B Port] PT1 Pressure Minus Limit Error",
            0
        ),

        # A Port Motion Control Alarms (301-396)
        301: (
            "[A Port] 체결 모터 이상",
            "[A Port] Coupler Unit Servo Error",
            3
        ),
        302: (
            "[A Port] 회전 모터 이상",
            "[A Port] Turn Unit Servo Error",
            4
        ),
        303: (
            "[A Port] 상승/하강 모터 이상",
            "[A Port] Lift Unit Servo Error",
            4
        ),
        304: (
            "[A Port] 체결부 CGA 위치 이동 이상",
            "[A Port] CAP&CGA Unit CGA Position Off Check Error",
            3
        ),
        305: (
            "[A Port] 체결부 Turn 위치 이동 이상",
            "[A Port] CAP&CGA Unit Turn Position Off Check Error",
            3
        ),
        306: (
            "[A Port] 체결부 CAP 위치 이동 이상",
            "[A Port] CAP&CGA Unit CAP Position Off Check Error",
            3
        ),
        307: (
            "[A Port] 체결부 후진(도킹해제) 이상",
            "[A Port] CAP&CGA Unit Docking Cylinder Forward Off Check Error",
            3
        ),
        308: (
            "[A Port] 체결부 전진(도킹) 이상",
            "[A Port] CAP&CGA Unit Docking Cylinder Backward Off Check Error",
            3
        ),
        309: (
            "[A Port] 핸드밸브 연결실린더 전진 이상",
            "[A Port] Hand Valve Unit Gear Link On Check Error",
            2
        ),
        310: (
            "[A Port] 핸드밸브 Open/Close 실린더 우측 이동 이상",
            "[A Port] Hand Valve Unit CW Position Off Check Error",
            2
        ),
        311: (
            "[A Port] 핸드밸브 Open/Close 실린더 좌측 이동 이상",
            "[A Port] Hand Valve Unit CCW Position Off Check Error",
            2
        ),
        312: (
            "[A Port] 핸드밸브 Latch 실린더 연결 이상",
            "[A Port] Hand Valve Unit Latch Cylinder Forward On Check Error",
            2
        ),
        313: (
            "[A Port] 핸드밸브 Latch 실린더 해제 이상",
            "[A Port] Hand Valve Unit Latch Cylinder Forward Off Check Error",
            2
        ),
        314: (
            "[A Port] 핸드밸브 태엽 고정 실린더 해제 이상",
            "[A Port] Hand Valve Unit Gear Fixed Cylinder Backward Off Check Error",
            2
        ),
        315: (
            "[A Port] 핸드밸브 태엽 감기 실린더 감기 이상",
            "[A Port] Hand Valve Unit Spring Winding Cylinder Backward On Check Error",
            2
        ),
        316: (
            "[A Port] 가스켓 Unit 제거 위치 이동 이상",
            "[A Port] Gasket Unit Remove Position Off Check Error",
            3
        ),
        317: (
            "[A Port] 가스켓 Unit Plug 위치 이동 이상",
            "[A Port] Gasket Unit Plug Position Off Check Error",
            3
        ),
        318: (
            "[A Port] 가스켓 Unit Insert 위치 이동 이상",
            "[A Port] Gasket Unit Insert Position Off Check Error",
            3
        ),
        319: (
            "[A Port] 가스켓 Unit 가스켓 제거 이상",
            "[A Port] Gasket Unit Remove Error",
            3
        ),
        320: (
            "[A Port] 가스켓 Unit 전진 이상",
            "[A Port] Gasket Unit Cylinder Forward Off Check Error",
            3
        ),
        321: (
            "[A Port] 가스켓 Unit 후진 이상",
            "[A Port] Gasket Unit Cylinder Backward Off Check Error",
            3
        ),
        322: (
            "[A Port] 가스켓 Unit 삽입 피스톤 가스켓 없음 이상",
            "[A Port] Gasket Unit Gasket Empty Check Error",
            3
        ),
        323: (
            "[A Port] 가스켓 Unit 제거 피스톤 가스켓 Full 이상",
            "[A Port] Gasket Unit Gasket Full Check Error",
            3
        ),
        324: (
            "[A Port] 가스켓 Unit 가스켓 삽입 후 감지 이상",
            "[A Port] Gasket Unit Gasket Insert Off Check Error",
            3
        ),
        325: (
            "[A Port] 가스 실린더 CGA 감지 Fiber Sensor Front 이상",
            "[A Port] GAS Cylinder CGA Position Check Fiber Sensor Front Check Error",
            3
        ),
        326: (
            "[A Port] 가스 실린더 CGA 감지 Fiber Sensor Rear 이상",
            "[A Port] GAS Cylinder CGA Position Check Fiber Sensor Rear Check Error",
            3
        ),
        327: (
            "[A Port] 리프트 Unit 실린더 클램프 열기 이상",
            "[A Port] Lifter Unit Gas Cylinder Clamp Open Check Error",
            4
        ),
        328: (
            "[A Port] 리프트 Unit 실린더 클램프 잡기 이상",
            "[A Port] Lifter Unit Gas Cylinder Clamp Close Off Check Error",
            4
        ),
        329: (
            "[A Port] 리프트 Unit 실린더 회전테이블 고정 이상",
            "[A Port] Lifter Unit Gas Cylinder Turn Table Forward Off Check Error",
            4
        ),
        330: (
            "[A Port] 리프트 Unit 실린더 회전테이블 풀기 이상",
            "[A Port] Lifter Unit Gas Cylinder Turn Table Backward Off Check Error",
            4
        ),
        331: (
            "[A Port] 커플러 Unit 웨이트발란스 상승 이상",
            "[A Port] Coupler Unit Up/Down Cylinder Up Check Error",
            2
        ),
        332: (
            "[A Port] 캡 제거 이상",
            "[A Port] CAP&CGA Unit CAP Remove Error",
            3
        ),
        334: (
            "[A Port] 왼쪽 전장 박스 연기감지 이상",
            "[A Port] LEFT C_BOX Smoke Detect Error",
            1
        ),
        335: (
            "[A Port] Gas Cabinet EMS 감지 이상",
            "[A Port] Gas Cabinet EMS Off Check Error",
            1
        ),
        336: (
            "[A Port] CGA 체결 시간 초과 이상",
            "[A Port] CGA Contact Time Out Error",
            3
        ),
        337: (
            "[A Port] CAP 체결 시간 초과 이상",
            "[A Port] CAP Contact Time Out Error",
            3
        ),
        338: (
            "[A Port] 핸드밸브 열림 동작 인터락 횟수 초과 이상",
            "[A Port] Hand Valve Unit Valve Open Limit Count Over Error",
            2
        ),
        339: (
            "[A Port] Gasket 유무 확인 인터락 횟수 초과 이상",
            "[A Port] Gasket Unit Gasket Check Retry Limit Count Over Error",
            3
        ),
        340: (
            "[A Port] 핸드밸브 닫기 동작 인터락 횟수 초과 이상",
            "[A Port] Hand Valve Unit Valve Close Limit Count Over Error",
            2
        ),
        341: (
            "[A Port] 수평 얼라인 범위 초과 이상",
            "[A Port] CAP Align Range Over Error",
            3
        ),
        342: (
            "[A Port] 캡 오픈 중 밸브열림 명령 이상",
            "[A Port] CAP Open Interlock Error",
            3
        ),
        343: (
            "[A Port] 수평 얼라인 찾기 실패 이상",
            "[A Port] CAP Align Check Off Error",
            3
        ),
        344: (
            "[A Port] CAP&CGA 체결 Retry 횟수 초과 이상",
            "[A Port] CAP&CGA Connection Retry Count Over Error",
            3
        ),
        345: (
            "[A Port] 리프트 Unit 히터 접촉 실린더 전진 이상",
            "[A Port] Lift Unit Heater Plate Contact Forward Off Error",
            4
        ),
        346: (
            "[A Port] 리프트 Unit 히터 접촉 실린더 후진 이상",
            "[A Port] Lift Unit Heater Plate Contact Backward Off Error",
            4
        ),
        347: (
            "[A Port] 리프트 Unit 힌지 고정 실린더 전진 이상",
            "[A Port] Lift Unit Clamper Hinge Lock Forward Off Error",
            4
        ),
        348: (
            "[A Port] 리프트 Unit 힌지 고정 실린더 후진 이상",
            "[A Port] Lift Unit Clamper Hinge Lock Backward Off Error",
            4
        ),
        349: (
            "[A Port] 리프트 Unit Gas Cylinder 감지 이상",
            "[A Port] Gas Cylinder Loading Sensor Off Check Error",
            4
        ),
        350: (
            "[A Port] CGA 연결 Retry 횟수 초과 이상",
            "[A Port] CGA Docking Retry Count Over Error",
            3
        ),
        351: (
            "[A Port] Lifter 상승중 B면 Barrel Clamper Open 상태 이상",
            "[A Port] Lifter Up [B] Cylinder Clamp Open Error",
            4
        ),
        352: (
            "[A Port] 체결부 후진(도킹해제) 감지 이상",
            "[A Port] CAP&CGA Docking Cylinder Forward Error",
            3
        ),
        353: (
            "[A Port] 리프트 Unit 왼쪽 힌지 열림 감지 이상",
            "[A Port] Lifter Unit Left Hinge Open On Check Error",
            4
        ),
        354: (
            "[A Port] 리프트 Unit 오른쪽 힌지 열림 감지 이상",
            "[A Port] Lifter Unit Right Hinge Open On Check Error",
            4
        ),
        355: (
            "[A Port] 커플러 Unit 클램프 실린더 전진 이상",
            "[A Port] Auto Coupler Unit Clamp CYL Forward Off Check Error",
            2
        ),
        356: (
            "[A Port] 커플러 Unit 클램프 감지 이상",
            "[A Port] Auto Coupler Unit Clamp Off Check Error",
            2
        ),
        357: (
            "[A Port] 커플러 Unit 클램프 실린더 후진 이상",
            "[A Port] Auto Coupler Unit Clamp CYL Backward Off Check Error",
            2
        ),
        358: (
            "[A Port] 가스켓 Unit CGA Plug 전진 감지 이상",
            "[A Port] Gasket Unit CGA Plug Docking Forward On Check Error",
            3
        ),
        359: (
            "[A Port] 가스켓 Unit CGA Plug 전진 이상",
            "[A Port] Gasket Unit CGA Plug Docking Forward Off Check Error",
            3
        ),
        360: (
            "[A Port] 가스켓 Unit 가스켓 박스 감지 이상",
            "[A Port] Gasket Unit Gasket Box Off Check Error",
            3
        ),
        361: (
            "[A Port] 리프트 Unit 리프트 위치 이동 시간 초과 이상",
            "[A Port] Lift Unit Lift Position Move TimeOut Error",
            4
        ),
        362: (
            "[A Port] 가스켓 Unit 가스켓 박스 커버 열림 감지 이상",
            "[A Port] Gasket Unit Gasket Box Cover Off Check Error",
            3
        ),
        363: (
            "[A Port] 가스켓 Unit 가스켓 박스 커버 닫힘 감지 이상",
            "[A Port] Gasket Unit Gasket Box Cover On Check Error",
            3
        ),
        364: (
            "[A Port] 가스켓 Unit 가스켓 그립퍼 그립 감지 이상",
            "[A Port] Gasket Unit Gasket Gripper On Check Error",
            3
        ),
        365: (
            "[A Port] 가스켓 Unit 가스켓 그립퍼 그립 이상",
            "[A Port] Gasket Unit Gasket Gripper Off Check Error",
            3
        ),
        366: (
            "[A Port] 가스켓 Unit 가스켓 제거 횟수 초과 이상",
            "[A Port] Gasket Unit Gasket Remove Retry Count Over Error",
            3
        ),
        367: (
            "[A Port] 수직 얼라인 찾기 실패 이상",
            "[A Port] CAP Align Z Axis Off Check Error",
            3
        ),
        368: (
            "[A Port] Gas Cylinder 얼라인 감지 이상",
            "[A Port] Gas Cylinder Align Off Check Error",
            3
        ),
        369: (
            "[A Port] 리프트 Unit 턴 위치 이동 시간 초과 이상",
            "[A Port] Lift Unit Turn Position Move TimeOut Error",
            4
        ),
        370: (
            "[A Port] 비젼 Retry 횟수 초과 이상",
            "[A Port] Vision Retry Count Over Error",
            3
        ),
        371: (
            "[A Port] 핸드밸브 태엽 고정 실린더 후진 감지 이상",
            "[A Port] Hand Valve Unit Gear Fixed Cylinder Backward On Check Error",
            2
        ),
        372: (
            "[A Port] 체결부 후진(도킹해제) 감지 이상",
            "[A Port] CAP&CGA Unit Docking Cylinder Forward On Check Error",
            3
        ),
        373: (
            "[A Port] Plug 체결 시간 초과 이상",
            "[A Port] Plug Connection Timeout Error",
            3
        ),
        374: (
            "[A Port] 핸드밸브 밸브 저압 열기 인터락 횟수 초과 이상",
            "[A Port] Hand Valve Low Pressure Open Interlock Count Exceeded",
            2
        ),
        375: (
            "[A Port] 바코드 읽기 실패 이상",
            "[A Port] Barcode Read Failed",
            4
        ),
        393: (
            "[A Port] EtherCat 통신 이상",
            "[A Port] EtherCat Communication Error",
            1
        ),
        394: (
            "[A Port] EIP 통신 이상",
            "[A Port] EIP Communication Error",
            1
        ),
        395: (
            "[A Port] 상위 통신 이상",
            "[A Port] Upper Communication Error",
            1
        ),
        396: (
            "[A Port] 자동 도어 모터 이상",
            "[A Port] Auto Door Motor Error",
            1 
        ),
        401: (
            "[B Port] 체결 모터 이상",
            "[B Port] Coupler Unit Servo Error",
            6
        ),
        402: (
            "[B Port] 회전 모터 이상",
            "[B Port] Turn Unit Servo Error",
            7
        ),
        403: (
            "[B Port] 상승/하강 모터 이상",
            "[B Port] Lift Unit Servo Error",
            7
        ),
        404: (
            "[B Port] 체결부 CGA 위치 이동 이상",
            "[B Port] CAP&CGA Unit CGA Position Off Check Error",
            6
        ),
        405: (
            "[B Port] 체결부 Turn 위치 이동 이상",
            "[B Port] CAP&CGA Unit Turn Position Off Check Error",
            6
        ),
        406: (
            "[B Port] 체결부 CAP 위치 이동 이상",
            "[B Port] CAP&CGA Unit CAP Position Off Check Error",
            6
        ),
        407: (
            "[B Port] 체결부 후진(도킹해제) 이상",
            "[B Port] CAP&CGA Unit Docking Cylinder Forward Off Check Error",
            6
        ),
        408: (
            "[B Port] 체결부 전진(도킹) 이상",
            "[B Port] CAP&CGA Unit Docking Cylinder Backward Off Check Error",
            6
        ),
        409: (
            "[B Port] 핸드밸브 연결실린더 전진 이상",
            "[B Port] Hand Valve Unit Gear Link On Check Error",
            5
        ),
        410: (
            "[B Port] 핸드밸브 Open/Close 실린더 우측 이동 이상",
            "[B Port] Hand Valve Unit CW Position Off Check Error",
            5
        ),
        411: (
            "[B Port] 핸드밸브 Open/Close 실린더 좌측 이동 이상",
            "[B Port] Hand Valve Unit CCW Position Off Check Error",
            5
        ),
        412: (
            "[B Port] 핸드밸브 Latch 실린더 연결 이상",
            "[B Port] Hand Valve Unit Latch Cylinder Forward On Check Error",
            5
        ),
        413: (
            "[B Port] 핸드밸브 Latch 실린더 해제 이상",
            "[B Port] Hand Valve Unit Latch Cylinder Forward Off Check Error",
            5
        ),
        414: (
            "[B Port] 핸드밸브 태엽 고정 실린더 해제 이상",
            "[B Port] Hand Valve Unit Gear Fixed Cylinder Backward Off  Check Error",
            5
        ),
        415: (
            "[B Port] 핸드밸브 태엽 감기 실린더 감기 이상",
            "[B Port] Hand Valve Unit Spring Winding Cylinder Backward On Check Error",
            5
        ),
        416: (
            "[B Port] 가스켓 Unit 제거 위치 이동 이상",
            "[B Port] Gasket Unit Remove Position Off Check Error",
            6
        ),
        417: (
            "[B Port] 가스켓 Unit Plug 위치 이동 이상",
            "[B Port] Gasket Unit Plug Position Off Chek Error",
            6
        ),
        418: (
            "[B Port] 가스켓 Unit Insert 위치 이동 이상",
            "[B Port] Gasket Unit Insert Position Off Check Error",
            6
        ),
        419: (
            "[B Port] 가스켓 Unit 가스켓 제거 이상",
            "[B Port] Gasket Unit Removal Error",
            6
        ),
        420: (
            "[B Port] 가스켓 Unit 전진 이상",
            "[B Port] Gasket Unit Forward Off Check Error",
            6
        ),
        421: (
            "[B Port] 가스켓 Unit 후진 이상",
            "[B Port] Gasket Unit Backward Off Check Error",
            6
        ),
        422: (
            "[B Port] 가스켓 Unit 삽입 피스톤 가스켓 없음 이상",
            "[B Port] Gasket Unit Gasket Empty Check Error",
            6
        ),
        423: (
            "[B Port] 가스켓 Unit 제거 피스톤 가스켓 Full 이상",
            "[B Port] Gasket Unit Gasket Full Check Error",
            6
        ),
        424: (
            "[B Port] 가스켓 Unit 가스켓 삽입 후 감지 이상",
            "[B Port] Gasket Unit Gasket Insert Off Check Error",
            6
        ),
        425: (
            "[B Port] 가스 실린더 CGA 감지 Fiber Sensor Front 이상",
            "[B Port] GAS Cylinder CGA Position Check Fiber Sensor Front Check Error",
            6
        ),
        426: (
            "[B Port] 가스 실린더 CGA 감지 Fiber Sensor Rear 이상",
            "[B Port] GAS Cylinder CGA Position Check Fiber Sensor Rear Check Error",
            6
        ),
        427: (
            "[B Port] 리프트 Unit 실린더 클램프 열기 이상",
            "[B Port] Lifter Unit Gas Cylinder Clamp Open Check Error",
            7
        ),
        428: (
            "[B Port] 리프트 Unit 실린더 클램프 잡기 이상",
            "[B Port] Lifter Unit Gas Cylinder Clamp Close Off Check Error",
            7
        ),
        429: (
            "[B Port] 리프트 Unit 실린더 회전테이블 고정 이상",
            "[B Port] Lifter Unit Gas Cylinder Turn Table Forward Off Check Error",
            7
        ),
        430: (
            "[B Port] 리프트 Unit 실린더 회전테이블 풀기 이상",
            "[B Port] Lifter Unit Gas Cylinder Turn Table Backward Off Check Error",
            7
        ),
        431: (
            "[B Port] 커플러 Unit 웨이트발란스 상승 이상",
            "[B Port] Coupler Unit Up/Down Cylinder Up Check Error",
            5
        ),
        432: (
            "[B Port] 캡 제거 이상",
            "[B Port] CAP&CGA Unit CAP Remove Error",
            6
        ),
        434: (
            "[B Port] 왼쪽 전장 박스 연기감지 이상",
            "[B Port] Left Electrical Box Smoke Detection Error",
            1
        ),
        435: (
            "[B Port] Gas Cabinet EMS 감지 이상",
            "[B Port] Gas Cabinet EMS Detection Error",
            1
        ),
        436: (
            "[B Port] CGA 체결 시간 초과 이상",
            "[B Port] CGA Connection Timeout Error",
            6
        ),
        437: (
            "[B Port] CAP 체결 시간 초과 이상",
            "[B Port] CAP Connection Timeout Error",
            6
        ),
        438: (
            "[B Port] 핸드밸브 열림 동작 인터락 횟수 초과 이상",
            "[B Port] Hand Valve Open Operation Interlock Count Exceeded",
            5
        ),
        439: (
            "[B Port] Gasket 유무 확인 인터락 횟수 초과 이상",
            "[B Port] Gasket Check Interlock Count Exceeded",
            6
        ),
        440: (
            "[B Port] 핸드밸브 닫기 동작 인터락 횟수 초과 이상",
            "[B Port] Hand Valve Close Operation Interlock Count Exceeded",
            5
        ),
        441: (
            "[B Port] 수평 얼라인 범위 초과 이상",
            "[B Port] Horizontal Align Range Exceeded",
            6
        ),
        442: (
            "[B Port] 캡 오픈 중 밸브열림 명령 이상",
            "[B Port] Valve Open Command During Cap Opening Error",
            6
        ),
        443: (
            "[B Port] 수평 얼라인 찾기 실패 이상",
            "[B Port] Horizontal Align Search Failed",
            6
        ),
        444: (
            "[B Port] CAP&CGA 체결 Retry 횟수 초과 이상",
            "[B Port] CAP&CGA Connection Retry Count Exceeded",
            6
        ),
        445: (
            "[B Port] 리프트 Unit 히터 접촉 실린더 전진 이상",
            "[B Port] Lift Unit Heater Contact Cylinder Forward Error",
            7
        ),
        446: (
            "[B Port] 리프트 Unit 히터 접촉 실린더 후진 이상",
            "[B Port] Lift Unit Heater Contact Cylinder Backward Error",
            446
        ),
        447: (
            "[B Port] 리프트 Unit 힌지 고정 실린더 전진 이상",
            "[B Port] Lift Unit Hinge Lock Cylinder Forward Error",
            7
        ),
        448: (
            "[B Port] 리프트 Unit 힌지 고정 실린더 후진 이상",
            "[B Port] Lift Unit Hinge Lock Cylinder Backward Error",
            7
        ),
        449: (
            "[B Port] 리프트 Unit Gas Cylinder 감지 이상",
            "[B Port] Lift Unit Gas Cylinder Detection Error",
            7
        ),
        450: (
            "[B Port] CGA 연결 Retry 횟수 초과 이상",
            "[B Port] CGA Connection Retry Count Exceeded",
            6
        ),
        451: (
            "[B Port] Lifter 상승중 B면 Barrel Clamper Open 상태 이상",
            "[B Port] B Side Barrel Clamper Open During Lifter Rise Error",
            7
        ),
        452: (
            "[B Port] 체결부 후진(도킹해제) 감지 이상",
            "[B Port] Undocking Detection Error",
            6
        ),
        453: (
            "[B Port] 리프트 Unit 왼쪽 힌지 열림 감지 이상",
            "[B Port] Lift Unit Left Hinge Open Detection Error",
            7
        ),
        454: (
            "[B Port] 리프트 Unit 오른쪽 힌지 열림 감지 이상",
            "[B Port] Lift Unit Right Hinge Open Detection Error",
            7
        ),
        455: (
            "[B Port] 커플러 Unit 클램프 실린더 전진 이상",
            "[B Port] Coupler Unit Clamp Cylinder Forward Error",
            5
        ),
        456: (
            "[B Port] 커플러 Unit 클램프 감지 이상",
            "[B Port] Coupler Unit Clamp Detection Error",
            5
        ),
        457: (
            "[B Port] 커플러 Unit 클램프 실린더 후진 이상",
            "[B Port] Coupler Unit Clamp Cylinder Backward Error",
            5
        ),
        458: (
            "[B Port] 가스켓 Unit CGA Plug 전진 감지 이상",
            "[B Port] Gasket Unit CGA Plug Forward Detection Error",
            6
        ),
        459: (
            "[B Port] 가스켓 Unit CGA Plug 전진 이상",
            "[B Port] Gasket Unit CGA Plug Forward Error",
            6
        ),
        460: (
            "[B Port] 가스켓 Unit 가스켓 박스 감지 이상",
            "[B Port] Gasket Unit Gasket Box Detection Error",
            6
        ),
        461: (
            "[B Port] 리프트 Unit 리프트 위치 이동 시간 초과 이상",
            "[B Port] Lift Unit Position Movement Timeout Error",
            7
        ),
        462: (
            "[B Port] 가스켓 Unit 가스켓 박스 커버 열림 감지 이상",
            "[B Port] Gasket Unit Box Cover Open Detection Error",
            6
        ),
        463: (
            "[B Port] 가스켓 Unit 가스켓 박스 커버 닫힘 감지 이상",
            "[B Port] Gasket Unit Box Cover Close Detection Error",
            6
        ),
        464: (
            "[B Port] 가스켓 Unit 가스켓 그립퍼 그립 감지 이상",
            "[B Port] Gasket Unit Gripper Grip Detection Error",
            6
        ),
        465: (
            "[B Port] 가스켓 Unit 가스켓 그립퍼 그립 이상",
            "[B Port] Gasket Unit Gripper Grip Error",
            6
        ),
        466: (
            "[B Port] 가스켓 Unit 가스켓 제거 횟수 초과 이상",
            "[B Port] Gasket Unit Gasket Remove Count Exceeded",
            6
        ),
        467: (
            "[B Port] 수직 얼라인 찾기 실패 이상",
            "[B Port] Vertical Align Search Failed",
            6
        ),
        468: (
            "[B Port] Gas Cylinder 얼라인 감지 이상",
            "[B Port] Gas Cylinder Align Detection Error",
            6
        ),
        469: (
            "[B Port] 리프트 Unit 턴 위치 이동 시간 초과 이상",
            "[B Port] Lift Unit Turn Position Movement Timeout Error",
            7
        ),
        470: (
            "[B Port] 비젼 Retry 횟수 초과 이상",
            "[B Port] Vision Retry Count Exceeded",
            6
        ),
        471: (
            "[B Port] 핸드밸브 태엽 고정 실린더 후진 감지 이상",
            "[B Port] Hand Valve Spring Lock Cylinder Backward Detection Error",
            5
        ),
        472: (
            "[B Port] 체결부 후진(도킹해제) 감지 이상",
            "[B Port] Undocking Detection Error",
            6
        ),
        473: (
            "[B Port] Plug 체결 시간 초과 이상",
            "[B Port] Plug Connection Timeout Error",
            6
        ),
        474: (
            "[B Port] 핸드밸브 밸브 저압 열기 인터락 횟수 초과 이상",
            "[B Port] Hand Valve Low Pressure Open Interlock Count Exceeded",
            5
        ),
        475: (
            "[B Port] 바코드 읽기 실패 이상",
            "[B Port] Barcode Read Failed Error",
            7
        ),
        493: (
            "[B Port] EtherCat 통신 이상",
            "[B Port] EtherCat Communication Error",
            1
        ),
        494: (
            "[B Port] EIP 통신 이상",
            "[B Port] EIP Communication Error",
            1
        ),
        495: (
            "[B Port] 상위 통신 이상",
            "[B Port] Gas Cabinet Commucation Error",
            1
        ),
        496: (
            "[B Port] 자동 도어 모터 이상",
            "[B Port] Door Unit Servo Error",
            1
        )
    }
