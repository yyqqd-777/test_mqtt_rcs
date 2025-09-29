import time

from helper import *

FULL_VEL = 2000
FULL_ACC = 500
FULL_DEC = 500


robot_init_path = [100000, 101000, 0, 0]

robot_path = [
    ['LIFT', 0],
]


robot_init_path = [106000, 103000, 180, 0]

robot_path = [
    ['LIFT', 370],
    ['LIFT', 0],
    # ['MOVE', 105000, 103000, FULL_VEL, FULL_ACC, FULL_DEC],
    # ['SPIN', 90],
    # ['MOVE', 105000, 104000, FULL_VEL, FULL_ACC, FULL_DEC],
    # ['MOVE', 105000, 103000, FULL_VEL, FULL_ACC, FULL_DEC],
    # ['SPIN', 180],
    # ['MOVE', 105000, 103000, FULL_VEL, FULL_ACC, FULL_DEC],
    # ['MOVE', 106000, 103000, FULL_VEL, FULL_ACC, FULL_DEC],
]

# robot_init_path = [100000, 102000, 0, 0]

# robot_path = [
#     ['LIFT', 200],
#     ['LIFT', 0],
#     ['MOVE', 102000, 102000, FULL_VEL, FULL_ACC, FULL_DEC],
#     ['SPIN', 90],
#     ['MOVE', 102000, 103000, FULL_VEL, FULL_ACC, FULL_DEC],
#     ['MOVE', 102000, 102000, FULL_VEL, FULL_ACC, FULL_DEC],
#     ['SPIN', 0],
#     ['MOVE', 101000, 102000, FULL_VEL, FULL_ACC, FULL_DEC],
#     ['MOVE', 100000, 102000, FULL_VEL, FULL_ACC, FULL_DEC],
# ]


def main(args):

    print(args)

    ant = Ant(args.ant)
    helper = Helper(robot_list=[ant])
    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(host=args.server_ip, port=args.server_port,
                      username=args.username, password=args.password)
    mqtt_client.add_robot(ant.robot_label)

    ant.state_update_flag = False
    while ant.state_update_flag is False:
        time.sleep(1)

    while ant.state != "UNKNOWN" and ant.state != "IDLE":
        time.sleep(1)

    # init ant
    if ant.state == "UNKNOWN":
        msg = build_robot_command_set(ant.robot_label, "INIT")

        mqtt_client.publish(
            robot_label=ant.robot_label, topic=msg.topic, payload=msg.payload
        )
        time.sleep(3)

    # check robot init state
    while ant.state != "IDLE":
        time.sleep(1)

    # return

    for i in range(args.cycle_count):
        print(f"Iteration {i+1}")
        for path in robot_path:
            while ant.state != "IDLE":
                time.sleep(0.2)
            msg = build_ant_action_command_set(
                robot_label=ant.robot_label,
                init_pos=robot_init_path,
                command_param=[path]
            )
            last_command_label = msg.payload["robotCommands"][-1]["robotCommandLabel"]
            mqtt_client.publish(
                robot_label=ant.robot_label,
                topic=msg.topic,
                payload=msg.payload,
            )
            while helper.last_complete_command_label != last_command_label:
                time.sleep(0.2)
            if path[0] == 'LIFT':
                robot_init_path[3] = path[1]
            if path[0] == 'MOVE':
                robot_init_path[0] = path[1]
                robot_init_path[1] = path[2]
            if path[0] == 'SPIN':
                robot_init_path[2] = path[1]

        time.sleep(2)
    mqtt_client.stop()


if __name__ == '__main__':
    try:
        main(parse_args())
    except KeyboardInterrupt:
        pass
