import time

from helper import *

ENABLE_PI = False

if ENABLE_PI:
    import paramiko

FLOW_INIT_POS = 1347131
FULL_VEL = 1500
FULL_VEL_S = 1000
FULL_ACC = 500

M = Cell(1815, -1016)
PD1 = Cell(2610, -1770)
C1 = Cell(605, 0)
C2 = Cell(4330, 3658)
C3 = Cell(13785, 1016)
C4 = Cell(18815, 6198)


def load_path() -> list[(Cell, str)]:
    return [
        # (PD1, "right_load"),
        # (PD1, "right_unload"),
        (C1, "right_double_load"),
        (C2, "right_unload"),
        (C3, "right_load"),
        (C4, "right_unload"),
        (C4, "right_load"),
        (C3, "right_unload"),
        (C2, "right_load"),
        (C1, "right_double_unload"),
    ]


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

        cnt = 0
        while True:
            cnt += 1
            helper.log.info("=" * 20 + f"test {cnt}" + "=" * 20)
            for cell, action in load_path():
                # input(f"press key to process {cell}...")

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
                    # input(f"press key to process {action}...")

                    # do action
                    while True:
                        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
                            f"cd /home/orangepi/project/spyder_pull_box && python3 spyder_{
                                action}.py {FLOW_INIT_POS}"
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
