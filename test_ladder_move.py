import time

from helper import *

FULL_VEL = 1500
FULL_ACC = 500


def main(args):
    print(args)

    ladder = Ladder(args.ladder)
    helper = Helper(robot_list=[ladder])
    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(host=args.server_ip, port=args.server_port,
                      username=args.username, password=args.password)
    mqtt_client.add_robot(ladder.robot_label)

    test_case = [
        [0, FULL_VEL, FULL_ACC],
    ]

    try:
        # 机器人初始化
        while ladder.state != "IDLE":
            time.sleep(1)

        init_pos = ladder.position

        msg = build_ladder_move_command_set(
            ladder.robot_label, init_pos, test_case)

        mqtt_client.publish(robot_label=ladder.robot_label,
                            topic=msg.topic, payload=msg.payload)

        last_command_label = msg.payload["robotCommands"][-1]["robotCommandLabel"]

        while helper.last_complete_command_label != last_command_label:
            time.sleep(1)

    except KeyboardInterrupt:
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
