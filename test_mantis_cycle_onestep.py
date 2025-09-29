import time
from helper import *

FULL_VEL_X = 1500
FULL_VEL_Z = 1000

FULL_ACC_X = 500
FULL_ACC_Z = 500

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
        total_start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"=== 测试开始时间：{total_start_time} ===")

        for i in range(args.cycle_count):
            for idx, l in enumerate(HZ_CS006_003MT):
                mantis.state_update_flag = False
                while not mantis.state_update_flag:
                    time.sleep(0.05)

                init_pos_x = mantis.position_x
                init_pos_z = mantis.position_z

                test_case = [[
                    l[0], l[1],
                    FULL_VEL_X, FULL_VEL_Z,
                    FULL_ACC_X, FULL_ACC_Z
                ]]

                msg = build_mantis_move_command_set(
                    mantis.robot_label, init_pos_x, init_pos_z, test_case
                )

                last_command_label = msg.payload["robotCommands"][-1]["robotCommandLabel"]

                start = time.time()

                mqtt_client.publish(
                    robot_label=mantis.robot_label,
                    topic=msg.topic,
                    payload=msg.payload
                )

                # 等待机器人执行完毕
                while helper.complete_command[mantis.robot_label] != last_command_label:
                    time.sleep(0.05)

                end = time.time()

                print(
                    f"循环 {i+1}, 目标点 {idx+1}: "
                    f"到达 ({l[0]}, {l[1]}) 耗时 {end - start:.2f} 秒"
                )

        total_end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"=== 测试结束时间：{total_end_time} ===")

    except KeyboardInterrupt:
        mqtt_client.stop()

if __name__ == "__main__":
    main(parse_args())
