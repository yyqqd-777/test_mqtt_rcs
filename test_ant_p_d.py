import time

from helper import *

FULL_VEL = 2000
FULL_ACC = 500


def main(args):
    print(args)

    ant = Ant(args.ant)
    helper = Helper(robot_list=[ant])
    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(host=args.server_ip, port=args.server_port,
                      username=args.username, password=args.password)
    mqtt_client.add_robot(ant.robot_label)

    # 机器人移动
    # 初始位置：（x, y, orientation, lift_height）
    def test_pair_generator(pos):
        return [
            [
                (101655, 102539, 180, 0),
                (104354, pos, 180, 0),
                (105988, pos, 180, 0),
                (104354, pos, 180, 0),
            ],
            [
                [
                    ['MOVE', 103354, 102539, FULL_VEL, FULL_ACC],
                    ['SPIN', 270],
                    ['MOVE', 103354, pos, FULL_VEL, FULL_ACC],
                    ['SPIN', 180],
                    ['MOVE', 104354, pos, FULL_VEL, FULL_ACC]
                ],
                [
                    ['MOVE', 105254, pos, FULL_VEL, FULL_ACC],
                    ['LIFT', 100],
                    ['MOVE', 105988, pos, FULL_VEL, FULL_ACC],
                    ['LIFT', 0]
                ],
                [
                    ['LIFT', 100],
                    ['MOVE', 105254, pos, FULL_VEL, FULL_ACC],
                    ['MOVE', 104354, pos, FULL_VEL, FULL_ACC],
                    ['LIFT', 0]
                ],
                [
                    ['MOVE', 103354, pos, FULL_VEL, FULL_ACC],
                    ['SPIN', 90],
                    ['MOVE', 103354, 102539, FULL_VEL, FULL_ACC],
                    ['SPIN', 180],
                    ['MOVE', 101655, 102539, FULL_VEL, FULL_ACC],
                ]
            ]
        ]

    p_d_position = [
        108894, 109707, 110520,
        113924, 114737, 115550,
        118952, 119765, 120578,
        123982, 124795, 125608,
        129010, 129823, 130636,
        134040, 134853, 135666,
    ]

    test_case_pairs = [test_pair_generator(pos) for pos in p_d_position]

    # 机器人初始化
    while ant.state != "IDLE":
        msg = build_robot_command_set(ant.robot_label, "INIT")

        mqtt_client.publish(
            robot_label=ant.robot_label, topic=msg.topic, payload=msg.payload)

        time.sleep(2)

    try:
        for init_pos, test_cases in test_case_pairs:
            for init, t in zip(init_pos, test_cases):
                # input("press any key to proceed")

                msg = build_ant_action_command_set(ant.robot_label, init, t)

                last_command_label = msg.payload["robotCommands"][-1]["robotCommandLabel"]

                mqtt_client.publish(
                    robot_label=ant.robot_label, topic=msg.topic, payload=msg.payload)

                while helper.last_complete_command_label != last_command_label:
                    time.sleep(1)

    except KeyboardInterrupt:
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
