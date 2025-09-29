import time

from helper import *

ENABLE_LHD = True
FULL_VEL = 1500
FULL_VEL_S = 1200
FULL_ACC = 500

M = Cell(1815, -1016)
PD1 = Cell(2610, -1770)
# C1 = Cell(23240, -1016)
# C2 = Cell(25755, -508)
# C3 = Cell(28270, -508)
# C4 = Cell(28875, -1016)

C1 = Cell(8150, -1016)
C2 = Cell(10665, -508)
C3 = Cell(11270, -508)
C4 = Cell(13180, -1016)


def load_path() -> list[(Cell, str)]:
    return [
        # cell, load, forward, distance
        (C1, True, False, 804),
        (C2, False, False, 844),
        (C3, True, False, 804),
        (C4, False, False, 844),
        (C4, True, False, 804),
        (C3, False, False, 844),
        (C2, True, False, 804),
        (C1, False, False, 844),
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

    try:
        # check robot init state
        while spyder.state != "IDLE" or ladder.state != "IDLE":
            time.sleep(1)

        cnt = 0
        while True:
            cnt += 1
            helper.log.info("=" * 20 + f"test {cnt}" + "=" * 20)

            for cell, load, forward, distance in load_path():
                for robot in robot_list:
                    robot.state_update_flag = False

                # input(f"press key to process {cell}...")

                while any([robot.state_update_flag is False for robot in robot_list]):
                    time.sleep(0.05)

                init_cell = Cell(ladder.position, spyder.position)
                target_x = cell.x
                target_z = cell.get_load_pos() if load else cell.get_unload_pos()

                if abs(init_cell.z - target_z) > 5:
                    msg = build_spyder_move_command_set(
                        spyder.robot_label,
                        init_cell.z,
                        [[target_z, FULL_VEL_S, FULL_ACC]]
                    )

                    mqtt_client.publish(
                        robot_label=spyder.robot_label, topic=msg.topic, payload=msg.payload)

                    command_spyder = msg.payload["robotCommands"][-1]["robotCommandLabel"]
                else:
                    command_spyder = None

                if abs(init_cell.x - target_x) > 5:
                    msg = build_ladder_move_command_set(
                        ladder.robot_label, init_cell.x, [[target_x, FULL_VEL, FULL_ACC]])

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

                if ENABLE_LHD:
                    spyder.state_update_flag = False

                    # input(f"press key to process load = {load}, "
                    #       f"forward = {forward}, "
                    #       f"distance = {distance}...")

                    while not spyder.state_update_flag:
                        time.sleep(0.05)

                    init_pos = spyder.position

                    msg = build_spyder_action_command_set(
                        spyder.robot_label, init_pos, load, forward, distance)

                    mqtt_client.publish(
                        robot_label=spyder.robot_label, topic=msg.topic, payload=msg.payload)

                    last_command_label = msg.payload["robotCommands"][-1]["robotCommandLabel"]

                    while helper.last_complete_command_label != last_command_label:
                        time.sleep(0.05)

    except KeyboardInterrupt:
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
