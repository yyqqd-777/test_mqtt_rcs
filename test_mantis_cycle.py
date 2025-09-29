import time

from helper import *

FULL_VEL_X = 1500
FULL_VEL_Z = 1500

FULL_ACC_X = 1000
FULL_ACC_Z = 1000


def main(args):
    print(args)

    mantis = Mantis(args.mantis)
    helper = Helper(robot_list=[mantis])
    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(
        host=args.server_ip,
        port=args.server_port,
        username=args.username,
        password=args.password,
    )
    mqtt_client.add_robot(mantis.robot_label)

    try:
        for i in range(args.cycle_count):
            # print(f"Iteration {i+1}")
            for idx, l in enumerate(HZ_CS006_502MT):
                forward_time = backward_time = 0
                # print(
                #     f"testing BAY 0 to BAY {
                #         idx + 1}, start pos = {FIRST_BAY}, end x pos = {l[0]} z pos = {l[1]}, test cycle = {args.cycle_count}"
                # )

                mantis.state_update_flag = False
                while not mantis.state_update_flag:
                    time.sleep(0.05)

                init_pos_x = mantis.position_x
                init_pos_z = mantis.position_z
                test_case = [[l[0], l[1], FULL_VEL_X,
                             FULL_VEL_Z, FULL_ACC_X, FULL_ACC_Z]]

                msg = build_mantis_move_command_set(
                    mantis.robot_label, init_pos_x, init_pos_z, test_case
                )

                last_command_label = msg.payload["robotCommands"][-1][
                    "robotCommandLabel"
                ]

                start = time.time()

                mqtt_client.publish(
                    robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload
                )

                while helper.complete_command[mantis.robot_label] != last_command_label:
                    time.sleep(0.05)

                end = time.time()
                forward_time += end - start

                mantis.state_update_flag = False
                while not mantis.state_update_flag:
                    time.sleep(0.05)

                init_pos_x = mantis.position_x
                init_pos_z = mantis.position_z

                test_case = [[FIRST_BAY, FIRST_BAY,
                              FULL_VEL_X, FULL_VEL_Z, FULL_ACC_X, FULL_ACC_Z]]

                msg = build_mantis_move_command_set(
                    mantis.robot_label, init_pos_x, init_pos_z, test_case
                )

                last_command_label = msg.payload["robotCommands"][-1][
                    "robotCommandLabel"
                ]

                start = time.time()

                mqtt_client.publish(
                    robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload
                )

                while helper.complete_command[mantis.robot_label] != last_command_label:
                    time.sleep(0.05)

                end = time.time()
                backward_time += end - start

                # print(
                #     f"forward time avg = {
                #         forward_time / args.cycle_count}, backward time avg = {backward_time / args.cycle_count}"
                # )
            # print("sleeping")
            # time.sleep(1)

    except KeyboardInterrupt:
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
