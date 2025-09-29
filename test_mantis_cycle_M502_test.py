import time
from helper import *

FULL_VEL_X = 1500
FULL_VEL_Z = 1500

FULL_ACC_X = 1000
FULL_ACC_Z = 1000


def run_cycle_once(mantis, helper, mqtt_client, args, iteration):
    print(f"Iteration {iteration}")
    for idx, l in enumerate(HZ_CS006_002MT):
        forward_time = backward_time = 0
        print(f"testing BAY 0 to BAY {idx + 1}, start pos = {FIRST_BAY}, end x pos = {l[0]} z pos = {l[1]}")

        mantis.state_update_flag = False
        while not mantis.state_update_flag:
            time.sleep(0.05)

        init_pos_x = mantis.position_x
        init_pos_z = mantis.position_z
        test_case = [[l[0], l[1], FULL_VEL_X, FULL_VEL_Z, FULL_ACC_X, FULL_ACC_Z]]

        msg = build_mantis_move_command_set(
            mantis.robot_label, init_pos_x, init_pos_z, test_case
        )
        last_command_label = msg.payload["robotCommands"][-1]["robotCommandLabel"]

        start = time.time()
        mqtt_client.publish(
            robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload
        )
        while helper.complete_command[mantis.robot_label] != last_command_label:
            time.sleep(0.05)
        # time.sleep(8)  # 模拟拉还箱延时
        end = time.time()
        forward_time += end - start

        mantis.state_update_flag = False
        while not mantis.state_update_flag:
            time.sleep(0.05)

        init_pos_x = mantis.position_x
        init_pos_z = mantis.position_z
        test_case = [[FIRST_BAY, FIRST_BAY, FULL_VEL_X, FULL_VEL_Z, FULL_ACC_X, FULL_ACC_Z]]

        msg = build_mantis_move_command_set(
            mantis.robot_label, init_pos_x, init_pos_z, test_case
        )
        last_command_label = msg.payload["robotCommands"][-1]["robotCommandLabel"]

        start = time.time()
        mqtt_client.publish(
            robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload
        )
        while helper.complete_command[mantis.robot_label] != last_command_label:
            time.sleep(0.05)
        end = time.time()
        backward_time += end - start
        # time.sleep(8)  # 模拟拉还箱延时

        print(f"forward time = {forward_time:.2f}s, backward time = {backward_time:.2f}s")


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
        iteration = 1
        if args.cycle_count == -1:
            while True:
                run_cycle_once(mantis, helper, mqtt_client, args, iteration)
                iteration += 1
        else:
            for i in range(args.cycle_count):
                run_cycle_once(mantis, helper, mqtt_client, args, i + 1)
    except KeyboardInterrupt:
        print("Interrupted by user, stopping MQTT client.")
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
