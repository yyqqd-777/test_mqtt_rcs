import threading
import time

from helper import *

MAIN_LOG = True
ENABLE_PI = False

if ENABLE_PI:
    import paramiko

FULL_VEL_L = 1500
FULL_VEL_S = 1000
FULL_ACC = 500

FLOW_INIT_POS = 1347293
C1 = Cell(605, 0)
C2 = Cell(2620, -1770)  # P&D
C3 = Cell(13785, 1016)
C4 = Cell(12668, -1770)  # P&D
C5 = Cell(18815, 6198)
CHARGER = Node(101655, 102539, ori=180)  # CHARGER


def load_full_script() -> list[dict]:
    return [
        # STEP 1
        # - ANT GO TO P&D 1 AND DROP THE TOTE, THEN EXIT
        # - SPYDER GO TO C2 AND WAIT
        {
            "ANT": [
                # P&D - 1
                Node(103354, 102539),
                Node(103354, 108894),
                Node(105254, 108894, ori=180, lift=100),  # P&D
                Node(105988, 108894, ori=180, lift=0),  # P&D
            ],
            "LADDER_SPYDER": [
                (C2, "", 0),
            ],
        },
        # STEP 2
        # - SPYDER GO TO C2 AND PICK THE TOTE
        {
            "ANT": [
                Node(105254, 108894, ori=180, lift=0),  # P&D
            ],
            "LADDER_SPYDER": [
                (C2, "right_load", FLOW_INIT_POS),
            ],
        },
        # STEP 3
        # - SPYDER GO TO C1 AND DROP THE TOTE
        {
            "LADDER_SPYDER": [
                (C1, "right_double_unload", FLOW_INIT_POS),
            ],
        },
        # STEP 4
        # - ANT GO TO P&D 2 AND WAIT
        # - SPYDER GO TO C3 AND PICK THE TOTE, THEN GO TO C4 AND DROP THE TOTE
        {
            "ANT": [
                Node(103354, 108894),
                Node(103354, 118952),
                Node(105254, 118952),
            ],
            "LADDER_SPYDER": [
                (C3, "right_load", FLOW_INIT_POS),
                (C4, "right_unload", FLOW_INIT_POS),
            ],
        },
        # STEP 5
        # - ANT GO TO P&D 2 AND PICK THE TOTE, THEN EXIT FROM P&D 2
        # - SPYDER GO TO C5 AND WAIT
        {
            "ANT": [
                # P&D - 2
                Node(105988, 118952, ori=180, lift=100),  # P&D
                Node(105254, 118952, ori=180, lift=0),  # P&D
            ],
            "LADDER_SPYDER": [
                (C5, "", 0),
            ],
        },
        # STEP 6
        # RECOVER SITE
        # - SPYDER GO TO C1 AND PICK THE TOTE, THEN GO TO C3 AND DROP THE TOTE
        # - ANT GO TO CHARGER WITH THE TOTE
        {
            "ANT": [
                # CHARGER
                Node(103354, 118952),
                Node(103354, 102539),
                CHARGER,
            ],
            "LADDER_SPYDER": [
                (C1, "right_double_load", FLOW_INIT_POS),
                (C3, "right_unload", FLOW_INIT_POS),
            ],
        },
    ]


def ladder_spyder_task(ladder: Ladder, spyder: Spyder, path: list[tuple], mqtt_client: MQTTClient, helper: Helper, ssh):
    if not path:
        return

    for cell, action, flow_init_pos in path:
        # before next step, wait for robot state update
        while not ladder.state_update_flag or not spyder.state_update_flag:
            time.sleep(0.1)

        # generate the inti_cell
        init_cell = Cell(ladder.position, spyder.position)

        target_x = cell.x
        target_z = cell.z if not action else cell.get_unload_pos(
        ) if "unload" in action else cell.get_load_pos()

        # SPYDER MOVE START
        if abs(init_cell.z - target_z) > 5:
            msg = build_spyder_move_command_set(
                spyder.robot_label,
                init_cell.z,
                [[cell.get_unload_pos() if "unload" in action else cell.get_load_pos(
                ), FULL_VEL_S, FULL_ACC]],
                spyder.load_sensor_front,
                spyder.load_sensor_rear
            )

            mqtt_client.publish(
                robot_label=spyder.robot_label, topic=msg.topic, payload=msg.payload)

            command_spyder = msg.payload["robotCommands"][-1]["robotCommandLabel"]
        else:
            command_spyder = None

        # LADDER MOVE START
        if abs(init_cell.x - target_x) > 5:
            msg = build_ladder_move_command_set(
                ladder.robot_label, init_cell.x, [[cell.x, FULL_VEL_L, FULL_ACC]])

            mqtt_client.publish(
                robot_label=ladder.robot_label, topic=msg.topic, payload=msg.payload)

            command_ladder = msg.payload["robotCommands"][-1]["robotCommandLabel"]
        else:
            command_ladder = None

        while (
                (command_spyder and helper.complete_command[spyder.robot_label] != command_spyder)
                or
                (command_ladder and helper.complete_command[ladder.robot_label] != command_ladder)
        ):
            time.sleep(0.05)

        ladder.state_update_flag = False
        spyder.state_update_flag = False

        if ENABLE_PI:
            # input(f"press key to process {action}...")

            # do action
            while action:
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
                    f"cd /home/orangepi/project/spyder_pull_box && python3 spyder_{action}.py {flow_init_pos}"
                )
                exit_status = ssh_stdout.channel.recv_exit_status()  # Blocking call
                if exit_status:
                    helper.log_info(f"Error {exit_status}")
                else:
                    break


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
    ladder = Ladder(args.ladder)
    spyder = Spyder(args.spyder)
    robot_list: list[Robot] = [ant, ladder, spyder]

    helper = Helper(robot_list=robot_list, log_flag=MAIN_LOG)
    helper.log_info(args)

    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(host=args.server_ip, port=args.server_port,
                      username=args.username, password=args.password)

    mqtt_client.add_robot(ant.robot_label)
    mqtt_client.add_robot(ladder.robot_label)
    mqtt_client.add_robot(spyder.robot_label)

    ssh = None
    if ENABLE_PI:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("192.168.10.100", 22,
                    username="orangepi", password="orangepi")

    try:
        # wait for robot online and report their states
        while any([robot.state_update_flag is False for robot in robot_list]):
            time.sleep(1)

        # init ant
        while ant.state == "UNKNOWN":
            msg = build_robot_command_set(ant.robot_label, "INIT")

            mqtt_client.publish(
                robot_label=ant.robot_label, topic=msg.topic, payload=msg.payload)

            time.sleep(2)

        # check robot init state
        while any([robot.state != "IDLE" for robot in robot_list]):
            time.sleep(1)

        # start test
        cnt = 0
        while True:
            cnt += 1
            helper.log_info("=" * 20 + f"test {cnt}" + "=" * 20)
            for step in load_full_script():
                # input(f"press key to process {step}...")

                path_ant: list[Node] = step.get("ANT", [])  # list of Node
                path_ladder_spyder: list[tuple] = step.get("LADDER_SPYDER", [])

                # LADDER & SPYDER TASK START
                ladder_spyder_thread = threading.Thread(
                    target=ladder_spyder_task,
                    args=(ladder, spyder, path_ladder_spyder, mqtt_client, helper, ssh),
                    daemon=True
                )
                ladder_spyder_thread.start()

                # ANT TASK START
                ant_thread = threading.Thread(
                    target=ant_move_task, args=(ant, path_ant, mqtt_client, helper), daemon=True)
                ant_thread.start()

                while (
                        (ladder_spyder_thread.is_alive())
                        or
                        (ant_thread.is_alive())
                ):
                    time.sleep(0.05)

            # break

    except KeyboardInterrupt:
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
