import time
from enum import Enum

from helper import *

# 是否开启多层对原点
MULTI_FLAG = True

# 机器人对原点参数
# 第1层
FIRST_CODE_HEIGHT = 260  # mm
# 第2层
MULTI_CODE_HEIGHT = FIRST_CODE_HEIGHT + 600
HORIZONTAl_CODE_DISTANCE = 500  # mm

# Mantis对原点流程相关控制状态枚举
class STATE(Enum):
    # 初始状态，对Mantis发送INIT指令
    START = 0
    # 持续发送Spyder HOME_SPYDER_MOVE_SCAN指令，移动到distanceToDmCodes高度
    SPYDER_MOVE_SEEKING_CODE = 1
    # 读取并记录下方第一个码的X坐标
    GETTING_X_BOTTOM_POS = 5
    # 对Spyder发送HOME_SPYDER_MOVE指令，移动到上方第二个码的高度
    SPYDER_MOVE_TOP = 6
    # 读取并记录上方第二个码的X坐标
    GETTING_X_TOP_POS = 7
    # 对Ladder发送HOME_LADDER_ADJUST指令，进行校直
    LADDER_ADJUST = 8
    # 对Mantis发送HOME_SET_ORIGIN指令，设置originOffset（x/z）坐标
    SETTING_X_AND_Z_POS = 10
    # 对Spyder发送HOME_HANDLE指令，进行拉还箱机构对原点
    SPYDER_HOME_HANDLE = 11
    # 完成
    FINISHED = 20
    # 失败
    FAILED = 30
    # 报错
    ERROR = 40


def main(args):
    print(args)

    mantis = Mantis(args.mantis)
    helper = Helper(robot_list=[mantis])
    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(host=args.server_ip, port=args.server_port,
                      username=args.username, password=args.password)
    mqtt_client.add_robot(mantis.robot_label)

    try:
        home_state = STATE.START
        coord_x_top = coord_x_bottom = 0

        while True:
            print(home_state)

            if home_state == STATE.START:
                # wait robot to online
                while mantis.state != "UNKNOWN":

                    time.sleep(1)

                # send INIT
                msg = build_robot_command_set(
                    mantis.robot_label, "INIT")

                mqtt_client.publish(
                    robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload)

                # INIT complete
                while mantis.state != "LOCATION_UNKNOWN":
                    time.sleep(1)

                home_state = STATE.SPYDER_MOVE_SEEKING_CODE

            elif home_state == STATE.SPYDER_MOVE_SEEKING_CODE:
                msg = build_mantis_home_command_set(
                    mantis.robot_label, command_type="HOME_MANTIS_FIRST_CODE", distance_to_dm_codes=FIRST_CODE_HEIGHT, distance_between_dm_codes=HORIZONTAl_CODE_DISTANCE)

                last_command_label = msg.payload["robotCommands"][-1]["robotCommandLabel"]

                mqtt_client.publish(
                    robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload)

                while helper.complete_command[mantis.robot_label] != last_command_label:
                    time.sleep(0.01)

                for _ in range(3):
                    # ensure to get the latest scan_state of spyder
                    time.sleep(2)
                    if mantis.is_dm_code():
                        home_state = STATE.GETTING_X_BOTTOM_POS
                        break
                else:
                    home_state = STATE.FAILED

            elif home_state == STATE.GETTING_X_BOTTOM_POS:
                scan_data, offset_x = mantis.scan_data, mantis.scan_x
                if len(scan_data) == 16 and scan_data.isdigit():
                    coord_x_bottom = int(scan_data[:6]) + offset_x
                    print("code 1: ", scan_data, offset_x, coord_x_bottom)

                    home_state = STATE.SPYDER_MOVE_TOP if MULTI_FLAG else STATE.SETTING_X_AND_Z_POS
                else:
                    home_state = STATE.FAILED

            elif home_state == STATE.SPYDER_MOVE_TOP:
                msg = build_spyder_home_command_set(
                    mantis.robot_label, command_type="HOME_MANTIS_MULTI_CODE", distance_to_dm_codes=MULTI_CODE_HEIGHT)

                last_command_label = msg.payload["robotCommands"][-1]["robotCommandLabel"]

                mqtt_client.publish(
                    robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload)

                while helper.complete_command[mantis.robot_label] != last_command_label:
                    time.sleep(0.01)

                # ensure to get the latest scan_state of spyder
                for _ in range(3):
                    time.sleep(2)
                    if mantis.is_dm_code():
                        home_state = STATE.GETTING_X_TOP_POS
                        break
                else:
                    home_state = STATE.FAILED

            elif home_state == STATE.GETTING_X_TOP_POS:
                scan_data, offset_x = mantis.scan_data, mantis.scan_x
                if len(scan_data) == 16 and scan_data.isdigit():
                    coord_x_top = int(scan_data[:6]) + offset_x
                    print("code 2: ", scan_data, offset_x, coord_x_top)

                    home_state = STATE.LADDER_ADJUST
                else:
                    home_state = STATE.FAILED

            elif home_state == STATE.LADDER_ADJUST:
                distance_to_adjust = coord_x_bottom - coord_x_top
                print("distance_to_adjust: ", distance_to_adjust)
                msg = build_ladder_home_command_set(
                    # mantis.robot_label, command_type="HOME_MANTIS_ADJUST", distance_to_adjust=10)
                    mantis.robot_label, command_type="HOME_MANTIS_ADJUST", distance_to_adjust=distance_to_adjust)
                

                last_command_label = msg.payload["robotCommands"][-1]["robotCommandLabel"]

                mqtt_client.publish(
                    robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload)

                while helper.complete_command[mantis.robot_label] != last_command_label:
                    time.sleep(0.01)

                # ensure to get the latest scan_state of mantis
                for _ in range(3):
                    time.sleep(2)
                    if mantis.is_dm_code():
                        home_state = STATE.SETTING_X_AND_Z_POS
                        break
                else:
                    home_state = STATE.FAILED

            elif home_state == STATE.SETTING_X_AND_Z_POS:
                scan_data, offset_x, offset_z = mantis.scan_data, mantis.scan_x, mantis.scan_z
                if len(scan_data) == 16 and scan_data.isdigit():
                    coord_x = int(scan_data[:6]) + offset_x
                    coord_z = int(scan_data[6:11]) + offset_z
                    print(scan_data, offset_x, offset_z, coord_x, coord_z)

                    msg = build_mantis_home_command_set(
                        mantis.robot_label, command_type="HOME_SET_ORIGIN", origin_offset_x=coord_x, origin_offset_z=coord_z)

                    mqtt_client.publish(
                        robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload)

                    while mantis.state != "LOCATION_KNOWN":
                        time.sleep(1)

                    home_state = STATE.SPYDER_HOME_HANDLE
                else:
                    home_state = STATE.FAILED

            elif home_state == STATE.SPYDER_HOME_HANDLE:
                msg = build_home_command_set_simple(
                    mantis.robot_label, command_type="HOME_HANDLER")

                mqtt_client.publish(
                    robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload
                )

                while mantis.state != "IDLE":
                    time.sleep(1)

                home_state = STATE.FINISHED

            elif home_state == STATE.FAILED:
                print("=" * 20 + "FAILED" + "=" * 20)
                break

            elif home_state == STATE.FINISHED:
                print("=" * 20 + "COMPLETE" + "=" * 20)
                break

    except KeyboardInterrupt:
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
