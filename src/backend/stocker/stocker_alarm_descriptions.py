# alarms/stocker/stocker_descriptions.py
from typing import Dict, Tuple

def get_stocker_descriptions() -> Dict[int, Tuple[str, str, int]]:
    """
    Returns:
        Dict[int, Tuple[str, str, int]]: 
            key: 알람 코드
            value: (한글 설명, 영문 설명, display_number)
            알람표시번호는 엑셀칼럼에 있음. 번호 없으면 0으로 표시
    """
    return {
        # Emergency & Safety
        1: (
            "Emergency 버튼이 동작",
            "[Common] Emergency S/W On Error",
            1
        ),
        2: (
            "Door 열림 감지",
            "[Common] Sensing Door Open",
            1
        ),
        3: (
            "Main Air OFF 감지",
            "[Common] Sensing Main Air OFF",
            1
        ),
        4: (
            "[공통] Main MC OFF 감지",
            "[Common] Sensing Main MC OFF 감지",
            1
        ),
        # Motor Faults
        5: (
            "[공통] Motor # 0축 (X) Amp Fault Alarm",
            "[Common] Motor # Axis 0 (X) Amp Fault Alarm",
            2
        ),
        6: (
            "[공통] Motor # 1축 (Z) Amp Fault Alarm",
            "[Common] Motor # Axis 1 (Z) Amp Fault Alarm",
            2
        ),
        7: (
            "[공통] Motor # 2축 (Remove Turn) Amp Fault Alarm",
            "[Common] Motor # Axis 2 (Remove Turn) Amp Fault Alarm",
            2
        ),
        8: (
            "[공통] Motor # 3축 (Gripper Turn) Amp Fault Alarm", 
            "[Common] Motor # Axis 3 (Gripper Turn) Amp Fault Alarm",
            4
        ),
        9: (
            "[공통] Motor # 4축 (Left Door) Amp Fault Alarm",
            "[Common] Motor # Axis 4 (Left Door) Amp Fault Alarm",
            3
        ),
        10: (
            "[공통] Motor # 5축 (Right Door) Amp Fault Alarm",
            "[Common] Motor # Axis 5 (Right Door) Amp Fault Alarm",
            3
        ),
        11: (
            "[공통] Motor # 6축 (미정의) Amp Fault Alarm",
            "[Common] Motor # Axis 6 (undefine) Amp Fault Alarm",
            0
        ),
        12: (
            "[공통] Motor # 7축 (미정의)Amp Fault Alarm",
            "[Common] Motor # Axis 7 (undefined)Amp Fault Alarm",
            0
        ),
        13: (
            "[공통] Motor # 8축 (미정의) Amp Fault Alarm",
            "[Common] Motor # Axis 8 (undefined) Amp Fault Alarm",
            0
        ),
        14: (
            "[공통] Motor # 9축 (미정의) Amp Fault Alarm",
            "[Common] Motor # Axis 9 (undefined) Amp Fault Alarm",
            0
        ),
        # Initialization Errors
        15: (
            "[공통] 초기화가 정상적으로 완료되지 않음",
            "[Common] Initialization did not complete successfully",
            2
        ),
        16: (
            "[공통] 초기화 : Z 축 Home Check 이동 실패",
            "[Common] Initialization : Axis Z Home Check Fail",
            2
        ),
        17: (
            "[공통] 초기화 : X 축 Home Check 이동 실패",
            "[Common] Initialization : Axis X Home Check Fail",
            2
        ),
        18: (
            "[B Port] Front Cap Gripper 에 Cap 분리중 Cap 이 감지됨 이상  \n\r (CapUnscrew_CapInGripper_Check)",
            "[B Port] CapUnscrew in progress Cap sensing  by CapGripper.",
            2
        ),
        19: (
            "[B Port] 모터 #2 Axis(Z) 이 Cap 분리중 Safety 위치로 상승 이상 \n\r (CapUnscrew_AxisZ_Move_SafetyPos_Check)",
            "[B Port] CapUnscrew in Progress Axis Z Move Safety Position Error",
            2
        ),
        20: (
            "[B Port] 모터 #1 Axis(X) 이 Cap 분리중 Barrel (LD) 위치로 이동 이상 \n\r (CapUnscrew_AxisX_Move_BarrelPos_Check)",
            "[B Port] CapUnscrew in Progress Axis X Move Cylinder Position Error",
            2
        ),
        21: (
            "[B Port] Cap 분리중 Barrel 이 감지 불가 이상. \n\r  (CapUnscrew_BarrelExist_Check)",
            "[B Port] CapUnscrew in progress Cylinder did not Sensed Error",
            4
        ),
        22: (
            "[B Port] Cap 분리중 Cap 의 Top 위치 찾기 실패 \n\r (CapUnscrew_AxisZ_CapSearch_Check)",
            "[B Port] CapUnscrew in Progress CapGripper did not find Top Position of the Cap Error",
            2
        ),
        23: (
            "[B Port] 모터 #2 Axis(Z) 이 Cap 분리 준비 위치로 하강 이상 \n\r (CapUnscrew_AxisZ_Move_ReadyPos_Check)",
            "[B Port] CapUnscrew in Progress Axis Z move Ready Position Error",
            2
        ),
        24: (
            "[B Port] 모터 #2 Axis(Z) 이 Cap 분리 너트 체결위치로 하강 이상 \n\r (CapUnscrew_AxisZ_Move_InsertPos_Check)",
            "[B Port] CapUnscrew in Progress Axis Z move Insert Position Error",
            2
        ),
        25: (
            "[B Port] 모터 #3 Axis(Rotator) 이 Cap 분리 Cap 열기시작 토크에 도달하지 못함 \n\r (CapUnscrew_AxisR_ReleseTorque_Check)",
            "[B Port] CapUnscrew in Progress Axis CapRotator Failed to reach the set opening torque",
            2
        ),
        26: (
            "[B Port] 모터 #2 Axis(Z) 이 Cap 분리 분리위치로 상승 이상 \n\r (CapUnscrew_AxisZ_Move_SeperatePos_Check)",
            "[B Port] CapUnscrew in Progress Axis Z move Separate Position Error",
            2
        ),
        29: (
            "[B Port] Cap 체결 중 Gripper 에 Cap 감지 이상 \n\r ( CapScrew_CheckCapExist )",
            "[B Port] CapScrew in Progress Cap sensing  by CapGripper.",
            2
        ),
        30: (
            "[B Port] 모터 #2 Axis(Z) 이 Safety 위치로 상승 이상 \n\r (CapScrew_AxisZ_Move_SafetyPos_Check)",
            "[B Port] CapScrew in Progress Axis Z Move Safety Position Error",
            2
        ),
        31: (
            "[B Port] 모터 #1 Axis(X) 이 Barrel (LD) 위치로 이동 이상 \n\r (CapScrew_AxisX_Move_BarrelPos_Check)",
            "[B Port] CapScrew in Progress Axis X Move Cylinder Position Error",
            2
        ),
        32: (
            "[B Port] Cap 체결중 Barrel 이 감지 불가 이상.  \n\r  (CapScrew_BarrelExist_Check)",
            "[B Port] CapScrew in progress Cylinder did not Sensed Error",
            4
        ),
        33: (
            "[B Port] 모터 #2 Axis(Z) 이 Cap 체결 준비 위치로 하강 이상 \n\r (CapScrew_AxisZ_Move_ReadyPos_Check)",
            "[B Port] CapScrew in Progress Axis Z move Ready Position Error",
            2
        ),
        34: (
            "[B Port] 모터 #2 Axis(Z) 이 Cap 체결중 Barrel Neck 감지 불가 이상 \n\r (CapScrew_AxisZ_BarrelNeckSearch_Check)",
            "[B Port] CapScrew in Progress CapGripper did not find neck Position of the Cap Error",
            2
        ),
        35: (
            "[B Port] 모터 #2 Axis(Z) 이 Cap 체결 위치로 하강 이상 \n\r (CapScrew_AxisZ_Move_InsertPos_Check)",
            "[B Port] CapScrew in Progress Axis Z move Insert Position Error",
            2
        ),
        36: (
            "[B Port] 모터 #3 Axis(Rotator) 이  Cap 체결 Cap의 닫기 토크에 도달하지 못함 \n\r (CapScrew_AxisR_CloseTorque_Check)",
            "[B Port] CapScrew in Progress Axis CapRotator Failed to reach the set closing torque",
            2
        ),
        37: (
            "[B Port] 모터 #2 Axis(Z)이 Cap 체결 Safety 위치로 상승 이상 \n\r (CapScrew_AxisZ_Move_SafetyPos2)",
            "[B Port] Axis Z Move Safety Position After CapScrew Progress Error",
            2
        ),
        52: (
            "[B Port] Rgv LD BarrelExist Check 중 Barrel 감지. \n\r (Rgv_LD_BarrelExist_Check)",
            "[B Port] AGV LD Cylinder Detected in the BarrelExist Check Error",
            4
        ),
        53: (
            "[B Port] Rgv LD Door Open Check 동작 중 LD Door Open 이상 감지. \n\r (Rgv_LD_Door_Open_Check)",
            "[B Port] AGV LD in Progress Bunker Door Open ckeck Error",
            3
        ),
        54: (
            "[B Port] Rgv LD BarrelDetected Check 중 Barrel 미감지. \n\r (Rgv_LD_BarrelDetected_Check)",
            "[B Port] AGV LD Cylinder did not Detect in the BarrelDetect Check",
            4
        ),
        55: (
            "[B Port] Rgv LD Door Close check 동작 중 LD Door Close 이상 감지. \n\r (Rgv_LD_Door_Close_check)",
            "[B Port] AGV LD in Progress Bunker Door Close ckeck Error",
            3
        ),
        56: (
            "[B Port] Rgv ULD BarrelExist  Check 중 Barrel 감지. \n\r (Rgv_ULD_BarrelExist_Check)",
            "[B Port] AGV ULD Cylinder Detected in the BarrelExist Check Error",
            4
        ),
        57: (
            "[B Port] Rgv ULD Door Open Check 동작 중 LD Door Open 이상 감지. \n\r (Rgv_ULD_Door_Open_Check)",
            "[B Port] AGV ULD in Progress Bunker Door Open ckeck Error",
            3
        ),
        58: (
            "[B Port] Rgv ULD BarrelDetected Check 중 Barrel 미감지. \n\r (Rgv_ULD_BarrelDetected_Check)",
            "[B Port] AGV LD Cylinder did not Detect in the BarrelDetect Check",
            4
        ),
        59: (
            "[B Port] Rgv ULD Door Close check 동작 중 LD Door Close 이상 감지. \n\r (Rgv_ULD_Door_Close_check)",
            "[B Port] AGV ULD in Progress Bunker Door Close ckeck Error",
            3
        ),
        60: (
            "[B Port] Barrel 얼라인 중에 Load 부 얼라인을 위한 회전에 실패했습니다. \n\r(BarrelAlign_LdBarrelAlign_Rotate_Check)",
            "[B Port] Cylinder Alingment rotation fail",
            4
        ),
        74: (
            "[공통] X0000_BUNKER_EMS_ON_CHK 감지 이상",
            "[Common] X0000_BUNKER_EMS_ON_CHK Detection Error",
            1
        ),
        75: (
            "[공통] X0001_BUNKER_MODE_SWITCH_WORKER_CHK 감지 이상",
            "[Common]X0001_BUNKER_MODE_SWITCH_WORKER_CHK Detection Error",
            1
        ),
        76: (
            "[공통] X0002_BUNKER_MODE_SWITCH_REAR_CHK 감지 이상",
            "[Common]X0002_BUNKER_MODE_SWITCH_REAR_CHK Detection Error",
            1
        ),
        77: (
            "[공통] X0003_BUNKER_OPEN_SWITCH_CHK 감지 이상",
            "[Common]X0003_BUNKER_OPEN_SWITCH_CHK Detection Error",
            1
        ),
        78: (
            "[공통] X0004_BUNKER_CLOSE_SWITCH_CHK 감지 이상",
            "[Common] X0004_BUNKER_CLOSE_SWITCH_CHK Detection Error",
            1
        ),
        79: (
            "[공통] X0005_BUNKER_S_RESET_SWITCH_CHK 감지 이상",
            "[Common] X0005_BUNKER_S_RESET_SWITCH_CHK Detection Error",
            1
        ),
        80: (
            "[공통] X0006_BUNKER_BUZZER_OFF_SWITCH_CHK 감지 이상",
            "[Common] X0006_BUNKER_BUZZER_OFF_SWITCH_CHK Detection Error",
            1
        ),
        81: (
            "[공통] X0007_WORKER_EMS_ON_CHK 감지 이상",
            "[Common] X0007_WORKER_EMS_ON_CHK Detection Error",
            1
        ),
        82: (
            "[공통] X0008_WORKER_MODE_SWITCH_FRONT_CHK 감지 이상",
            "[Common] X0008_WORKER_MODE_SWITCH_FRONT_CHK Detection Error",
            1
        ),
        83: (
            "[공통] X0009_WORKER_MODE_SWITCH_BUNKER_CHK 감지 이상",
            "[Common] X0009_WORKER_MODE_SWITCH_BUNKER_CHK Detection Error",
            1
        ),
        84: (
            "[공통] X000A_WORKER_OPEN_SWITCH_CHK 감지 이상",
            "[Common] X000A_WORKER_OPEN_SWITCH_CHK Detection Error",
            1
        ),
        85: (
            "[공통] X000B_WORKER_CLOSE_SWITCH_CHK 감지 이상",
            "[Common] X000B_WORKER_CLOSE_SWITCH_CHK Detection Error",
            1
        ),
        86: (
            "[공통] X000C_WORKER_S_RESET_SWITCH_CHK 감지 이상",
            "[Common] X000C_WORKER_S_RESET_SWITCH_CHK Detection Error",
            1
        ),
        87: (
            "[공통] X000D_WORKER_BUZZER_OFF_SWITCH_CHK 감지 이상",
            "[Common] X000D_WORKER_BUZZER_OFF_SWITCH_CHK Detection Error",
            1
        ),
        88: (
            "[공통] X000E_NA 감지 이상",
            "[Common] X000E_NA Detection Error",
            0
        ),
        89: (
            "[공통] X000F_NA 감지 이상",
            "[Common] X000F_NA Detection Error",
            0
        ),
        90: (
            "[공통] X0010_SMOKE_SENSOR_ON_CHK 감지 이상",
            "[Common] X0010_SMOKE_SENSOR_ON_CHK Detection Error",
            1
        ),
        91: (
            "[공통] X0011_REGULATOR_SENSOR_ON_CHK 감지 이상",
            "[Common] X0011_REGULATOR_SENSOR_ON_CHK Detection Error",
            1
        ),
        92: (
            "[공통] X0012_MC_ON_CHK 감지 이상",
            "[Common] X0012_MC_ON_CHK Detection Error",
            1
        ),
        93: (
            "[공통] X0013_SAFETY_UNIT_ON_CHK 감지 이상",
            "[Common] X0013_SAFETY_UNIT_ON_CHK Detection Error",
            1
        ),
        94: (
            "[공통] X0014_PIO_SIGNAL_GO 감지 이상",
            "[Common] X0014_PIO_SIGNAL_GO Detection Error",
            1
        ),
        95: (
            "[공통] X0015_PIO_CS_PORT_A Detection 감지 이상",
            "[Common] X0015_PIO_CS_PORT_A Detection Error",
            1
        ),
        96: (
            "[공통] X0016_PIO_CS_PORT_B 감지 이상",
            "[Common] X0016_PIO_CS_PORT_B Detection Error",
            1
        ),
        97: (
            "[공통] X0017_PIO_NA 감지 이상",
            "[Common] X0017_PIO_NA Detection Error",
            1
        ),
        98: (
            "[공통] X0018_PIO_NA 감지 이상",
            "[Common] X0018_PIO_NA Detection Error",
            1
        ),
        99: (
            "[공통] X0019_PIO_VALID 감지 이상",
            "[Common] X0019_PIO_VALID Detection Error",
            1
        ),
        100: (
            "[공통] X001A_PIO_COMPLETE 감지 이상",
            "[Common] X001A_PIO_COMPLETE Detection Error",
            1
        ),
        101: (
            "[공통] X001B_PIO_DOOR_OPEN_REQUEST 감지 이상",
            "[Common] X001B_PIO_DOOR_OPEN_REQUEST Detection Error",
            1
        ),
        102: (
            "[공통] X001C_PIO_DOOR_CLOSE_REQUEST 감지 이상",
            "[Common] X001C_PIO_DOOR_CLOSE_REQUEST Detection Error",
            1
        ),
        103: (
            "[공통] X001D_NA 감지 이상",
            "[Common] X001D_NA Detection Error",
            0
        ),
        104: (
            "[공통] X001E_NA 감지 이상",
            "[Common] X001E_NA Detection Error",
            0
        ),
        105: (
            "[공통] X001F_NA 감지 이상",
            "[Common] X001F_NA Detection Error",
            0
        ),
        106: (
            "[A Port] X0020_NA 감지 이상",
            "[A Port] X0020_NA Detection Error",
            0
        ),
        107: (
            "[A Port] X0021_NA 감지 이상",
            "[A Port] X0021_NA Detection Error",
            0
        ),
        108: (
            "[B Port] X0022_NA 감지 이상",
            "[B Port] X0022_NA Detection Error",
            0
        ),
        109: (
            "[B Port] X0023_NA 감지 이상",
            "[B Port] X0023_NA Detection Error",
            0
        ),
        110: (
            "[B Port] X0024_BUNKER_LD_DR_OP_STATUS 감지 이상",
            "[B Port] X0024_BUNKER_LD_DR_OP_STATUS Detection Error",
            3
        ),
        111: (
            "[B Port] X0025_BUNKER_LD_DR_CL_STATUS 감지 이상",
            "[B Port] X0025_BUNKER_LD_DR_CL_STATUS Detection Error",
            3
        ),
        112: (
            "[A Port] X0026_BUNKER_ULD_DR_OP_STATUS 감지 이상",
            "[A Port] X0026_BUNKER_ULD_DR_OP_STATUS Detection Error",
            3
        ),
        113: (
            "[A Port] X0027_BUNKER_ULD_DR_CL_STATUS 감지 이상",
            "[A Port] X0027_BUNKER_ULD_DR_CL_STATUS Detection Error",
            3
        ),
        114: (
            "[B Port] X0028_NA 감지 이상",
            "[B Port] X0028_NA Detection Error",
            0
        ),
        115: (
            "[B Port] X0029_NA 감지 이상",
            "[B Port] X0029_NA Detection Error",
            0
        ),
        116: (
            "[B Port] X002A_NA 감지 이상",
            "[B Port] X002A_NA Detection Error",
            0
        ),
        117: (
            "[B Port] X002B_NA 감지 이상",
            "[B Port] X002B_NA Detection Error",
            0
        ),
        118: (
            "[A Port] X002C_NA 감지 이상",
            "[A Port] X002C_NA Detection Error",
            0
        ),
        119: (
            "[A Port] X002D_NA 감지 이상",
            "[A Port] X002D_NA Detection Error",
            0
        ),
        120: (
            "[A Port] X002E_NA 감지 이상",
            "[A Port] X002E_NA Detection Error",
            0
        ),
        121: (
            "[A Port] X002F_NA 감지 이상",
            "[A Port] X002F_NA Detection Error",
            0
        ),
        122: (
            "[B Port] X0030_BUNKER_LD_DOOR_HEAD_CYL_FWD 감지 이상",
            "[B Port] X0030_BUNKER_LD_DOOR_HEAD_CYL_FWD Detection Error",
            3
        ),
        123: (
            "[B Port] X0031_BUNKER_LD_DOOR_HEAD_CYL_BWD 감지 이상",
            "[B Port] X0031_BUNKER_LD_DOOR_HEAD_CYL_BWD Detection Error",
            3
        ),
        124: (
            "[A Port] X0032_BUNKER_ULD_DOOR_HEAD_CYL_FWD 감지 이상",
            "[A Port] X0032_BUNKER_ULD_DOOR_HEAD_CYL_FWD Detection Error",
            3
        ),
        125: (
            "[A Port] X0033_BUNKER_ULD_DOOR_HEAD_CYL_BWD 감지 이상",
            "[A Port] X0033_BUNKER_ULD_DOOR_HEAD_CYL_BWD Detection Error",
            3
        ),
        126: (
            "[B Port] X0034_BUNKER_LD_DOOR_LEFT_BOT_CYL_FWD 감지 이상",
            "[B Port] X0034_BUNKER_LD_DOOR_LEFT_BOT_CYL_FWD Detection Error",
            3
        ),
        127: (
            "[B Port] X0035_BUNKER_LD_DOOR_LEFT_BOT_CYL_BWD 감지 이상",
            "[B Port] X0035_BUNKER_LD_DOOR_LEFT_BOT_CYL_BWD Detection Error",
            3
        ),
        128: (
            "[B Port] X0036_BUNKER_LD_DOOR_RIGHT_BOT_CYL_FWD 감지 이상",
            "[B Port] X0036_BUNKER_LD_DOOR_RIGHT_BOT_CYL_FWD Detection Error",
            3
        ),
        129: (
            "[B Port] X0037_BUNKER_LD_DOOR_RIGHT_BOT_CYL_BWD 감지 이상",
            "[B Port] X0037_BUNKER_LD_DOOR_RIGHT_BOT_CYL_BWD Detection Error",
            3
        ),
        130: (
            "[A Port] X0038_BUNKER_ULD_DOOR_LEFT_BOT_CYL_FWD 감지 이상",
            "[A Port] X0038_BUNKER_ULD_DOOR_LEFT_BOT_CYL_FWD Detection Error",
            3
        ),
        131: (
            "[A Port] X0039_BUNKER_ULD_DOOR_LEFT_BOT_CYL_BWD 감지 이상",
            "[A Port] X0039_BUNKER_ULD_DOOR_LEFT_BOT_CYL_BWD Detection Error",
            3
        ),
        132: (
            "[A Port] X003A_BUNKER_ULD_DOOR_RIGHT_BOT_CYL_FWD 감지 이상",
            "[A Port] X003A_BUNKER_ULD_DOOR_RIGHT_BOT_CYL_FWD Detection Error",
            3
        ),
        133: (
            "[A Port] X003B_BUNKER_ULD_DOOR_RIGHT_BOT_CYL_BWD 감지 이상",
            "[A Port] X003B_BUNKER_ULD_DOOR_RIGHT_BOT_CYL_BWD Detection Error",
            3
        ),
        134: (
            "[B Port] X003C_NA 감지 이상",
            "[B Port] X003C_NA Detection Error",
            0
        ),
        135: (
            "[B Port] X003D_NA 감지 이상",
            "[B Port] X003D_NA Detection Error",
            0
        ),
        136: (
            "[A Port] X003E_NA 감지 이상",
            "[A Port] X003E_NA Detection Error",
            0
        ),
        137: (
            "[A Port] X003F_NA 감지 이상",
            "[A Port] X003F_NA Detection Error",
            0
        ),
        138: (
            "[B Port] X0040_LD_LEFT_GRIPPER_CYL_FWD 감지 이상",
            "[B Port] X0040_LD_LEFT_GRIPPER_CYL_FWD Detection Error",
            2
        ),
        139: (
            "[B Port] X0041_LD_LEFT_GRIPPER_CYL_BWD 감지 이상",
            "[B Port] X0041_LD_LEFT_GRIPPER_CYL_BWD Detection Error",
            2
        ),
        140: (
            "[B Port] X0042_LD_RIGHT_GRIPPER_CYL_FWD 감지 이상",
            "[B Port] X0042_LD_RIGHT_GRIPPER_CYL_FWD Detection Error",
            2
        ),
        141: (
            "[B Port] X0043_LD_RIGHT_GRIPPER_CYL_BWD 감지 이상",
            "[B Port] X0043_LD_RIGHT_GRIPPER_CYL_BWD Detection Error",
            2
        ),
        142: (
            "[B Port] X0044_GRIPPER_UNIT_GUIDE_BAR_CYL_FWD 감지 이상",
            "[B Port] X0044_GRIPPER_UNIT_GUIDE_BAR_CYL_FWD Detection Error",
            4
        ),
        143: (
            "[B Port] X0045_GRIPPER_UNIT_GUIDE_BAR_CYL_BWD 감지 이상",
            "[B Port] X0045_GRIPPER_UNIT_GUIDE_BAR_CYL_BWD Detection Error",
            4
        ),
        144: (
            "[B Port] X0046_LD_TURN_TABLE_CYL_1_LOCK 감지 이상",
            "[B Port] X0046_LD_TURN_TABLE_CYL_1_LOCK Detection Error",
            4
        ),
        145: (
            "[B Port] X0047_LD_TURN_TABLE_CYL_1_UNLOCK 감지 이상",
            "[B Port] X0047_LD_TURN_TABLE_CYL_1_UNLOCK Detection Error",
            4
        ),
        146: (
            "[B Port] X0048_LD_TURN_TABLE_CYL_2_LOCK 감지 이상",
            "[B Port] X0048_LD_TURN_TABLE_CYL_2_LOCK Detection Error",
            4
        ),
        147: (
            "[B Port] X0049_LD_TURN_TABLE_CYL_2_UNLOCK 감지 이상",
            "[B Port] X0049_LD_TURN_TABLE_CYL_2_UNLOCK Detection Error",
            4
        ),
        148: (
            "[B Port] X004A_GRIPPER_GAS_CYL_CHK 감지 이상",
            "[B Port] X004A_GRIPPER_GAS_CYL_CHK Detection Error",
            4
        ),
        149: (
            "[A Port] X004B_NA 감지 이상",
            "[A Port] X004B_NA Detection Error",
            0
        ),
        150: (
            "[A Port] X004C_NA 감지 이상",
            "[A Port] X004C_NA Detection Error",
            0
        ),
        151: (
            "[A Port] X004D_NA 감지 이상",
            "[A Port] X004D_NA Detection Error",
            0
        ),
        152: (
            "[A Port] X004E_NA 감지 이상",
            "[A Port] X004E_NA Detection Error",
            0
        ),
        153: (
            "[A Port] X004F_NA 감지 이상",
            "[A Port] X004F_NA Detection Error",
            0
        ),
        154: (
            "[공통] X0050_FRONT_CAP_GRIP_GUIDE_CYL_FWD 감지 이상",
            "[Common] X0050_FRONT_CAP_GRIP_GUIDE_CYL_FWD Detection Error",
            2
        ),
        155: (
            "[공통] X0051_FRONT_CAP_GRIP_GUIDE_CYL_BWD 감지 이상",
            "[Common] X0051_FRONT_CAP_GRIP_GUIDE_CYL_BWD Detection Error",
            2
        ),
        156: (
            "[공통] X0052_REAR_CAP_GRIP_GUIDE_CYL_FWD 감지 이상",
            "[Common] X0052_REAR_CAP_GRIP_GUIDE_CYL_FWD Detection Error",
            2
        ),
        157: (
            "[공통] X0053_REAR_CAP_GRIP_GUIDE_CYL_BWD 감지 이상",
            "[Common] X0053_REAR_CAP_GRIP_GUIDE_CYL_BWD Detection Error",
            2
        ),
        158: (
            "[공통] X0054_CAP_OPEN_CLOSE_CYL_UP 감지 이상",
            "[Common] X0054_CAP_OPEN_CLOSE_CYL_UP Detection Error",
            2
        ),
        159: (
            "[공통] X0055_CAP_OPEN_CLOSE_CYL_DOWN 감지 이상",
            "[Common] X0055_CAP_OPEN_CLOSE_CYL_DOWN Detection Error",
            2
        ),
        160: (
            "[공통] X0056_UNIT_FRONT_CAP_CHK 감지 이상",
            "[Common] X0056_UNIT_FRONT_CAP_CHK Detection Error",
            2
        ),
        161: (
            "[공통] X0057_UNIT_FRONT_NECKRING_EDGE_CHK 감지 이상",
            "[Common] X0057_UNIT_FRONT_NECKRING_EDGE_CHK Detection Error",
            2
        ),
        162: (
            "[공통] X0058_VISION_UNIT_CYL_UP 감지 이상",
            "[Common] X0058_VISION_UNIT_CYL_UP Detection Error",
            2
        ),
        163: (
            "[공통] X0059_VISION_UNIT_CYL_DOWN 감지 이상",
            "[Common] X0059_VISION_UNIT_CYL_DOWN Detection Error",
            2
        ),
        164: (
            "[A Port] X005A_NA 감지 이상",
            "[A Port] X005A_NA Detection Error",
            0
        ),
        165: (
            "[A Port] X005B_NA 감지 이상",
            "[A Port] X005B_NA Detection Error",
            0
        ),
        166: (
            "[A Port] X005C_NA 감지 이상",
            "[A Port] X005C_NA Detection Error",
            0
        ),
        167: (
            "[A Port] X005D_NA 감지 이상",
            "[A Port] X005D_NA Detection Error",
            0
        ),
        168: (
            "[공통] X005E_CAP REMOVE GRIPPER CHK 감지 이상",
            "[Common] X005E_CAP REMOVE GRIPPER CHK Detection Error",
            2
        ),
        169: (
            "[공통] X005F_NA 감지 이상",
            "[Common] X005F_NA Detection Error",
            0
        )
    }
