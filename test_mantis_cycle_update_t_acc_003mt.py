import time
from helper import *

# ===========================
# 全局运动参数配置
# ===========================
FULL_VEL_X = 1500  # 梯子方向（X 轴）运行速度
FULL_VEL_Z = 1500  # 蜘蛛方向（Z 轴）运行速度

FULL_ACC_X = 1000  # 梯子方向加速度
FULL_ACC_Z = 1000  # 蜘蛛方向加速度


def main(args):
    """
    程序入口函数
    负责初始化机器人、通信模块，并根据参数决定执行循环测试模式
    """
    print(args)  # 打印传入的命令行参数，便于调试

    # 初始化机器人对象（螳螂机器人）
    mantis = Mantis(args.mantis)

    # 创建辅助工具类，内部维护机器人列表和状态
    helper = Helper(robot_list=[mantis])

    # 初始化 MQTT 客户端，并绑定回调函数（用于接收机器人状态）
    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(
        host=args.server_ip,
        port=args.server_port,
        username=args.username,
        password=args.password,
    )
    mqtt_client.add_robot(mantis.robot_label)  # 注册机器人标签，便于消息收发

    try:
        # 记录测试开始时间
        total_start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"=== 测试开始时间：{total_start_time} ===")

        iteration = 0  # 记录循环次数

        # ========== 循环控制 ==========
        # 无限循环模式
        if args.cycle_count == -1:
            while True:
                iteration += 1
                run_one_cycle(mantis, helper, mqtt_client, iteration)
        else:
            # 固定循环次数模式
            for i in range(args.cycle_count):
                run_one_cycle(mantis, helper, mqtt_client, i + 1)

        # 记录测试结束时间
        total_end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        print(f"=== 测试结束时间：{total_end_time} ===")

    except KeyboardInterrupt:
        # 手动中断（Ctrl+C）
        print("\n=== 手动中断测试 ===")
        mqtt_client.stop()


def run_one_cycle(mantis, helper, mqtt_client, iteration):
    """
    执行单次完整循环
    包含：
    - 等待机器人状态更新
    - 计算初始位置
    - 构造运动命令
    - 发送 MQTT 控制消息
    - 等待执行完成并记录耗时
    """
    for idx, l in enumerate(HZ_CS006_003MT_T_ACC):  # 移动路径存放于 helper.py
        # ========== 等待机器人状态更新 ==========
        mantis.state_update_flag = False
        while not mantis.state_update_flag:
            time.sleep(0.05)

        # 记录机器人当前位置（执行命令的起点）
        init_pos_x = mantis.position_x
        init_pos_z = mantis.position_z

        # 组装测试指令：目标点 + 速度 + 加速度
        test_case = [[
            l[0], l[1],             # 目标坐标 (X, Z)
            FULL_VEL_X, FULL_VEL_Z, # 运行速度
            FULL_ACC_X, FULL_ACC_Z  # 加速度
        ]]
        # time.sleep(16) #动作延时

        # 构建螳螂机器人运动指令集（MQTT 消息）
        msg = build_mantis_move_command_set(
            mantis.robot_label, init_pos_x, init_pos_z, test_case, sCurve_profile=True
        )

        # 获取最后一条指令的标识符，用于后续确认执行完成
        last_command_label = msg.payload["robotCommands"][-1]["robotCommandLabel"]

        # ========== 下发控制命令 ==========
        start = time.time()
        mqtt_client.publish(
            robot_label=mantis.robot_label,
            topic=msg.topic,
            payload=msg.payload
        )

        # ========== 等待执行完成 ==========
        # 当 helper 记录的完成指令标识符 == 当前发送的最后指令时，表示动作完成
        while helper.complete_command[mantis.robot_label] != last_command_label:
            time.sleep(0.05)

        time.sleep(8) #动作延时
        end = time.time()

        # 输出执行结果：循环次数、目标点坐标、耗时
        print(
            f"循环 {iteration}, 目标点 {idx+1}: "
            f"到达 ({l[0]}, {l[1]}) 耗时 {end - start:.2f} 秒"
        )

if __name__ == "__main__":
    # 从命令行解析参数并执行主函数
    main(parse_args())
