import time

from helper import *


def main(args):
    print(args)

    mantis = Mantis(args.mantis)
    helper = Helper(robot_list=[mantis])
    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(host=args.server_ip, port=args.server_port,
                      username=args.username, password=args.password)
    mqtt_client.add_robot(mantis.robot_label)

    test_cases = [
        # target > 0 FORWARD, target < 0 BACKWARD
        # ["ARTICULATE_FINGERS", 9000, 0, 9000, 0, 9000, 0, 9000, 0],
        ["ARTICULATE_FINGERS", 0, 0, 0, 0, 0, 0, 0, 0],
        ["MOVE_ARMS", 1420, 1000, 1000],
        ["ARTICULATE_FINGERS", 0, 9000, 0, 9000, 0, 9000, 0, 9000],
        # ["ARTICULATE_FINGERS", 0, 0, 0, 0, 0, 0, 0, 0],
        ["MOVE_ARMS", 0, 1000, 1000],
        # ["ARTICULATE_FINGERS", 0, 9000, 0, 9000, 0, 9000, 0, 9000],
        # ["MOVE_ARMS", 130, 500, 500],
        # ["MOVE_ARMS", -270, 500, 500],
        ["ARTICULATE_FINGERS", 0, 0, 0, 0, 0, 0, 0, 0],
        ["MOVE_ARMS", 1460, 1000, 1000],
        ["ARTICULATE_FINGERS", 9000, 9000, 9000, 9000, 9000, 9000, 9000, 9000],
        ["MOVE_ARMS", 0, 1000, 1000],
        # ["MOVE_ARMS", 0, 500, 500],
    ]
    last_arm_position = 0
    try:
        while True:
            mantis.state_update_flag = False
            while not mantis.state_update_flag:
                time.sleep(0.05)
            commands = []
            for test_case in test_cases:
                if test_case[0] == "MOVE_ARMS":
                    tmp_msg = build_move_arms_command_set_simple(
                        robot_label=mantis.robot_label,
                        arm_position=test_case[1],
                        max_velocity=test_case[2],
                        max_acceleration=test_case[3],
                        expect={"armPosition": last_arm_position,
                                "armPositionTolerance": 10},
                        future={"armPosition": test_case[1],
                                "armPositionTolerance": 10}
                    )  # 可以根据希望判断的状态自行添加
                    last_arm_position = test_case[1]
                elif test_case[0] == "ARTICULATE_FINGERS":
                    tmp_msg = build_articulate_fingers_command_set_simple(
                        robot_label=mantis.robot_label,
                        pos=test_case[1:9],
                        expect={"armPosition": last_arm_position,   
                                "armPositionTolerance": 10,
                                "endOfArmSensors":{           #手臂传感器
                                #     "rearRightInner":False,    #右后侧内部
                                #     "rearRightOuter":False,    #右后侧外部
                                #     "rearLeftInner":False,     #左后侧内部
                                #     "rearLeftOuter":False,     #左后侧外部
                                #     "frontRightInner":False,   #右前侧内部
                                #     "frontRightOuter":False,   # 右前侧外部
                                #     "frontLeftInner":False,    #左前侧内部
                                #    "frontLeftOuter":False     #左前侧外部
                                    },   
                                },
                        future={"fingerPosition": {
                                "left1": test_case[1],
                                "right1": test_case[5]
                                },
                                "fingerPositionTolerance": 300,
                
                                "endOfArmSensors":{           #手臂传感器
                                #     "rearRightInner":False,    #右后侧内部
                                #     "rearRightOuter":False,    #右后侧外部
                                #     "rearLeftInner":False,     #左后侧内部
                                #     "rearLeftOuter":False,     #左后侧外部
                                #     "frontRightInner":False,   #右前侧内部
                                #     "frontRightOuter":False,   # 右前侧外部
                                #     "frontLeftInner":False,    #左前侧内部
                                #    "frontLeftOuter":False     #左前侧外部
                                    },
                                
                                })
                commands.append(tmp_msg.payload["robotCommands"][0])
            msg = build_general_command_set_multiple(
                robot_label=mantis.robot_label, commands=commands)
            mqtt_client.publish(
                robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload)

            last_command_label = msg.payload["robotCommands"][-1]["robotCommandLabel"]

            while helper.last_complete_command_label != last_command_label:
                time.sleep(1)

    except KeyboardInterrupt:
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
