import itertools
import time

from helper import *

ENABLE_PI = False

if ENABLE_PI:
    import paramiko

FLOW_INIT_POS = 1347061
FULL_VEL = 1500
FULL_VEL_S = 1200
FULL_ACC = 500


def load_cell(start_bay, end_bay, start_level, end_level) -> list[Cell]:
    col = [column for bay in C103_COLUMN[start_bay - 1:end_bay]
           for column in bay]
    row = C103_LEVEL[start_level - 1:end_level]

    return [
        Cell(x, z) for z, x in itertools.product(row, col)
    ]


def generate_path_continue():
    manual_cell = load_cell(1, 2, 1, 2)
    monkey_cell = load_cell(3, 4, 1, 15)

    while monkey_cell:
        path = []
        for manual, monkey in zip(manual_cell, monkey_cell):
            path += [
                (manual, "right_load"),
                (monkey, "right_unload")
            ]
        cnt = len(path) // 2
        monkey_cell = monkey_cell[cnt:]
        print(path)
        input(f"press key to process continue...")
        yield path
    print("test completed")


def main(args):
    print(args)

    spyder = Spyder(args.spyder)
    ladder = Ladder(args.ladder)
    robot_list = [spyder, ladder]

    helper = Helper(robot_list=robot_list)
    helper.log.info(args)

    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(host=args.server_ip, port=args.server_port,
                      username=args.username, password=args.password)

    mqtt_client.add_robot(spyder.robot_label)
    mqtt_client.add_robot(ladder.robot_label)

    if ENABLE_PI:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect("192.168.10.101", 22,
                    username="orangepi", password="orangepi")

    try:
        # check robot init state
        while spyder.state != "IDLE" or ladder.state != "IDLE":
            time.sleep(1)

        for path in generate_path_continue():
            for cell, action in path:
                while any([robot.state_update_flag is False for robot in robot_list]):
                    time.sleep(0.05)

                init_cell = Cell(ladder.position, spyder.position)

                if abs(init_cell.z - cell.z) > 5:
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

                if abs(init_cell.x - cell.x) > 5:
                    msg = build_ladder_move_command_set(
                        ladder.robot_label, init_cell.x, [[cell.x, FULL_VEL, FULL_ACC]])

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

                for robot in robot_list:
                    robot.state_update_flag = False

                if ENABLE_PI:
                    # do action
                    while True:
                        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
                            f"cd /home/orangepi/project/spyder_pull_box && python3 spyder_{action}.py {FLOW_INIT_POS}"
                        )
                        exit_status = ssh_stdout.channel.recv_exit_status()  # Blocking call
                        if exit_status:
                            helper.log.error(f"Error {exit_status}")
                        else:
                            break

    except KeyboardInterrupt:
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
