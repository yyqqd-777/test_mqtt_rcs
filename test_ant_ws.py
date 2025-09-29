import threading
import time

from helper import *

MAIN_LOG = True
CHARGER = Node(101655, 102539, ori=180)  # CHARGER


def load_path():
    """
    定义行走路径，单条路径包含的点位不建议超过5个，消息过长可能导致机器人无法正常接收
    """
    return [
        # WORKSTATION - PICK
        [
            Node(103354, 102539, ori=180),
            Node(104363, 102539, lift=0),
            Node(104363, 101696, ori=90, lift=100),
            Node(104363, 102539, ori=90, lift=0),
        ],
        # P&D - 1
        [
            Node(103354, 102539),
        ],
        # WORKSTATION - DROP
        [
            Node(104363, 102539, lift=100),
            Node(104363, 101696, ori=90, lift=0),
            Node(104363, 102539, ori=90, lift=0),
        ],
        # head back
        [
            Node(103354, 102539),
            CHARGER,
        ]
    ]


def load_ant_gen_2_path() -> list[Node]:
    return [
        [
            # Node(108472, 104362, ori=270),
            Node(111052, 104362),
            Node(111052, 106360),
            Node(109317, 106360, lift=0),  # pos_x: 109321  pos_y: 106364
            Node(108547, 106360, lift=270),  # pos_x: 108551  pos_y: 106361
        ],
        [
            Node(109317, 106360, lift=0),
            Node(111052, 106360),
            Node(111052, 104362),
            Node(108472, 104362),
        ],
        [
            # Node(108472, 104362, ori=270),
            Node(111052, 104362),
            Node(111052, 106360),
            Node(109317, 106360, lift=270),
            Node(108547, 106360, lift=0),  # pos_x: 108551  pos_y: 106361
        ],
        [
            Node(109317, 106360, lift=0),
            Node(111052, 106360),
            Node(111052, 104362),
            Node(108472, 104362),
        ]
    ]


def load_ant_ws_1_path() -> list[Node]:
    return [
        [
            # Node(109322, 105185, ori=270),
            Node(109322, 104362, ori=270),
            # PD1
            Node(109322, 102539, ori=270, lift=270),
            Node(109322, 101696, ori=270, lift=270),
            Node(109322, 102539, ori=270, lift=270),
        ],
        [
            # PD2
            Node(109927, 102539, lift=270),
            Node(109927, 101696, ori=270, lift=270),
            Node(109927, 102539, ori=270, lift=270),
        ],
        [
            # PD3
            Node(110532, 102539, lift=270),
            Node(110532, 101696, ori=270, lift=270),
            Node(110532, 102539, ori=270, lift=270),
        ],
        [
            # PD4
            Node(111292, 102539, lift=270),
            Node(111292, 101696, ori=270, lift=270),
            Node(111292, 102539, ori=270, lift=270),
        ],
        [
            # PD5
            Node(111897, 102539, lift=270),
            Node(111897, 101696, ori=270, lift=270),
            Node(111897, 102539, ori=270, lift=270),
        ],
        [
            # PD6
            Node(112502, 102539, lift=270),
            Node(112502, 101696, ori=270, lift=270),
            Node(112502, 102539, ori=270, lift=270),
        ],
        [
            Node(109322, 102539),
            Node(109322, 105185, ori=270)
        ]
    ]


def load_ant_ws_2_path() -> list[Node]:
    return [
        [
            Node(109322, 104362, ori=270),
            Node(106783, 104362),
            # PD1
            Node(106783, 102539, ori=270, lift=270),
            Node(106783, 101696, ori=270, lift=270),
            Node(106783, 102539, ori=270, lift=270),
        ],
        [
            # PD2
            Node(106178, 102539, lift=270),
            Node(106178, 101696, ori=270, lift=270),
            Node(106178, 102539, ori=270, lift=270),
        ],
        [
            # PD3
            Node(105573, 102539, lift=270),
            Node(105573, 101696, ori=270, lift=270),
            Node(105573, 102539, ori=270, lift=270),
        ],
        [
            # PD4
            Node(104813, 102539, lift=270),
            Node(104813, 101696, ori=270, lift=270),
            Node(104813, 102539, ori=270, lift=270),
        ],
        [
            # PD5
            Node(104208, 102539, lift=270),
            Node(104208, 101696, ori=270, lift=270),
            Node(104208, 102539, ori=270, lift=270),
        ],
        [
            # PD6
            Node(103603, 102539, lift=270),
            Node(103603, 101696, ori=270, lift=270),
            Node(103603, 102539, ori=270, lift=270),
        ],
        [
            Node(106783, 102539),
            Node(106783, 104362),
            Node(109322, 104362),
            Node(109322, 105185, ori=270)
        ]
    ]


def load_ant_ws_new_path() -> list[Node]:
    return [
        [
            Node(110172, 104362, ori=270),
            Node(102515, 104362),
        ],
        [
            # PD1
            Node(102515, 131525, lift=160),
            Node(101775, 131525, ori=180, lift=0),
        ],
        [
            Node(101775, 131525, ori=180, lift=160),
            Node(102515, 131525, ori=180, lift=0),
        ],
        [
            # PD2
            Node(102515, 132338, lift=160),
            Node(101775, 132338, ori=180, lift=0),
        ],
        [
            Node(101775, 132338, ori=180, lift=160),
            Node(102515, 132338, ori=180, lift=0),
        ],
        [
            # PD3
            Node(102515, 133151, lift=160),
            Node(101775, 133151, ori=180, lift=0),
        ],
        [
            Node(101775, 133151, ori=180, lift=160),
            Node(102515, 133151, ori=180, lift=0),
        ]
    ]


def ant_move_task(ant: Ant, path: list[Node], mqtt_client: MQTTClient, helper):
    if not path:
        return

    # get the latest ant state
    ant.state_update_flag = False
    while not ant.state_update_flag:
        time.sleep(0.1)

    # generate the init_node
    init_node = Node(ant.position_x, ant.position_y,
                     ant.orientation / 100, ant.height)

    full_path = find_full_path([init_node] + path)

    msg = build_ant_action_command_set(
        ant.robot_label, init_node.get_state(), full_path)

    command_ant = msg.payload["robotCommands"][-1]["robotCommandLabel"]

    mqtt_client.publish(
        robot_label=ant.robot_label, topic=msg.topic, payload=msg.payload)

    while helper.complete_command[ant.robot_label] != command_ant:
        time.sleep(0.05)


def main(args):
    print(args)

    ant = Ant(args.ant)
    robot_list = [ant]

    helper = Helper(robot_list=robot_list, log_flag=MAIN_LOG)
    helper.log_info(args)

    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(host=args.server_ip, port=args.server_port,
                      username=args.username, password=args.password)

    mqtt_client.add_robot(ant.robot_label)

    try:
        # wait for robot online and report its state
        while ant.state_update_flag is False:
            time.sleep(0.1)

        # init ant
        while ant.state == "UNKNOWN":
            msg = build_robot_command_set(ant.robot_label, "INIT")

            mqtt_client.publish(
                robot_label=ant.robot_label, topic=msg.topic, payload=msg.payload)

            time.sleep(2)

        # check robot init state
        while ant.state != "IDLE":
            time.sleep(1)

        # start test
        for path in load_ant_ws_new_path():
            # ANT TASK START
            ant_thread = threading.Thread(
                target=ant_move_task, args=(ant, path, mqtt_client, helper), daemon=True)
            ant_thread.start()

            while ant_thread.is_alive():
                time.sleep(0.05)

    except KeyboardInterrupt:
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
