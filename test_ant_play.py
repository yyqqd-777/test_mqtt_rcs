import time

from helper import *


def load_path():
    """
    定义行走路径，单条路径包含的点位不建议超过5个，消息过长可能导致机器人无法正常接收
    """
    return [
        [
            # Node(100000, 101000, ori=270, lift=270),
            # Node(100000, 101000, ori=270, lift=0),
            Node(102000, 101000, ori=270),
            Node(100000, 101000),
            Node(100000, 102000),
        ],
        [
            Node(101000, 102000),
            Node(101000, 101000),
            Node(102000, 101000),
        ],
        [
            Node(102000, 102000, ori=270),
        ]
    ]
    return [
        # walk out
        [
            Node(110532, 102539, ori=270),
            Node(112741, 102539),
            Node(112741, 105185),
        ],
        [
            Node(113641, 105185),
            Node(112741, 105185),
        ],
        # back to work station
        [
            Node(112741, 102539),
            Node(110532, 102539),
            Node(110532, 101696, ori=270),
        ]
    ]
    return [
        # P&D - 1
        [
            Node(102000, 108000),
            Node(107000, 108000),
            Node(107000, 112000),
            Node(103000, 108000),
        ],
        [
            Node(103000, 112000),
            Node(107000, 112000),
            Node(103000, 112000),
            Node(102000, 112000),
        ],
    ]


def main(args):
    print(args)

    ant = Ant(args.ant)
    helper = Helper(robot_list=[ant])
    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(
        host=args.server_ip,
        port=args.server_port,
        username=args.username,
        password=args.password,
    )
    mqtt_client.add_robot(ant.robot_label)

    try:
        # wait for robot online and report its state
        for i in range(args.cycle_count):
            print(f"Iteration {i+1}")
            while ant.state_update_flag is False:
                time.sleep(1)

            # init ant
            while ant.state == "UNKNOWN":
                msg = build_robot_command_set(ant.robot_label, "INIT")

                mqtt_client.publish(
                    robot_label=ant.robot_label, topic=msg.topic, payload=msg.payload
                )

                time.sleep(2)

            # check robot init state
            while ant.state != "IDLE":
                time.sleep(1)

            # start test
            for path in load_path():
                for node in path:
                    # get the latest ant state
                    ant.state_update_flag = False
                    while not ant.state_update_flag:
                        time.sleep(0.1)

                    # generate the init_node
                    init_node = Node(
                        ant.position_x,
                        ant.position_y,
                        ant.orientation / 100,
                        ant.height,
                    )

                    # find path from the init_node to node
                    commands = find_path(init_node, node)

                    msg = build_ant_action_command_set(
                        ant.robot_label, init_node.get_state(), commands
                    )

                    last_command_label = msg.payload["robotCommands"][-1][
                        "robotCommandLabel"
                    ]

                    mqtt_client.publish(
                        robot_label=ant.robot_label,
                        topic=msg.topic,
                        payload=msg.payload,
                    )

                    while helper.last_complete_command_label != last_command_label:
                        time.sleep(1)

    except KeyboardInterrupt:
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
