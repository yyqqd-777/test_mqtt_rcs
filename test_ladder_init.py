import time

from helper import *


def main(args):
    print(args)

    ladder = Ladder(args.ladder)
    helper = Helper(robot_list=[ladder])
    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(host=args.server_ip, port=args.server_port,
                      username=args.username, password=args.password)
    mqtt_client.add_robot(ladder.robot_label)

    try:
        # 机器人初始化
        while ladder.state != "UNKNOWN":
            time.sleep(1)

        msg = build_robot_command_set(ladder.robot_label, "INIT")

        mqtt_client.publish(
            robot_label=ladder.robot_label, topic=msg.topic, payload=msg.payload)

        while ladder.state != "LOCATION_UNKNOWN":
            time.sleep(1)

        msg = build_ladder_home_command_set(
            ladder.robot_label, command_type="HOME_LADDER_MOVE", distance_between_dm_codes=300)

        last_command_label = msg.payload["robotCommands"][-1]["robotCommandLabel"]

        mqtt_client.publish(
            robot_label=ladder.robot_label, topic=msg.topic, payload=msg.payload)

        while helper.complete_command[ladder.robot_label] != last_command_label:
            time.sleep(0.01)

        while ladder.state != "LOCATION_UNKNOWN":
            time.sleep(1)

        msg = build_ladder_home_command_set(
            ladder.robot_label, command_type="HOME_LADDER_ADJUST", distance_to_adjust=100)

        last_command_label = msg.payload["robotCommands"][-1]["robotCommandLabel"]

        mqtt_client.publish(
            robot_label=ladder.robot_label, topic=msg.topic, payload=msg.payload)

        while helper.complete_command[ladder.robot_label] != last_command_label:
            time.sleep(0.01)

        while ladder.state != "LOCATION_UNKNOWN":
            time.sleep(1)

        msg = build_ladder_home_command_set(
            ladder.robot_label, command_type="HOME_SET_ORIGIN", origin_offset=0)

        mqtt_client.publish(
            robot_label=ladder.robot_label, topic=msg.topic, payload=msg.payload)

        while ladder.state != "IDLE":
            time.sleep(1)

    except KeyboardInterrupt:
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
