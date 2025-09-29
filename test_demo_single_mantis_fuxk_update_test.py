import itertools
import threading
import time
import argparse
from helper import *

global FUXK_RUNNING
# 主线程与工作线程共享的运行开关：True 继续循环，False 停止
MAIN_LOG = True

# 是否开启拉还箱，False 关闭，True 开启
ENABLE_LHD = True

# 运动参数（默认值，可按需调整）
FULL_VEL_X = 1500 # x方向速度
FULL_VEL_Z = 1500 # z方向速度
FULL_ACC = 1000   # 加速度

# 拉还箱测试用例：按顺序执行的动作序列
# - MOVE_ARMS: 调整手臂位置，expect/future 定义传感器状态
# - ARTICULATE_FINGERS: 调整手指位置与间隙传感器期望
# 上箱测试用例：按顺序执行的动作序列
test_cases_load = [
    {"type": "ARTICULATE_FINGERS", "fingers": [0, 0, 0, 0, 0, 0, 0, 0]},
    {
        "type": "MOVE_ARMS", "arm_position": -760, "max_velocity": 1000, "max_acceleration": 1000,
        "expect": {
            "loadSensors": {"frontInner": False},
            # "endOfArmSensors": {"rearRightInner": False, "rearRightOuter": False, "rearLeftInner": False, "rearLeftOuter": False},
        },
        "future": {
            # "endOfArmSensors": {"rearRightInner": False, "rearRightOuter": False, "rearLeftInner": False, "rearLeftOuter": False},
        }
    },
    {"type": "ARTICULATE_FINGERS", "fingers": [9000, 0, 0, 0, 9000, 0, 0, 0]},
    {
        "type": "MOVE_ARMS", "arm_position": 20, "max_velocity": 800, "max_acceleration": 500,
        "expect": {"loadSensors": {"frontInner": False}},
        "future": {}
    },
    {
        "type": "MOVE_ARMS", "arm_position": 0, "max_velocity": 1000, "max_acceleration": 1000,
        "expect": {"loadSensors": {"frontInner": True}},
        "future": {"loadSensors": {"frontInner": True}},
    },
    {"type": "ARTICULATE_FINGERS", "fingers": [0, 0, 0, 0, 0, 0, 0, 0]},
]

# 下箱测试用例：按顺序执行的动作序列
test_cases_unload = [
    {"type": "ARTICULATE_FINGERS", "fingers": [0, 0, 0, 9000, 0, 0, 0, 9000]},
    {
        "type": "MOVE_ARMS", "arm_position": -800, "max_velocity": 800, "max_acceleration": 500,
        "expect": {
            "loadSensors": {"frontInner": True},
            # "endOfArmSensors": {"rearRightOuter": False, "rearRightInner": False, "rearLeftInner": False, "rearLeftOuter": False},
        },
        "future": {"loadSensors": {"frontInner": False}},
    },
    {"type": "MOVE_ARMS", "arm_position": 0, "max_velocity": 1000, "max_acceleration": 1000, "expect": {}, "future": {}},
    {"type": "ARTICULATE_FINGERS", "fingers": [0, 0, 0, 0, 0, 0, 0, 0]},
]

def load_shelf_hz_path() -> list[tuple[Cell, bool, bool, int]]:
    """
    生成上/入箱循环测试路径。
    返回: 列表 [(cell, load)]，其中 load=True 表示拉箱，load=False 表示还箱。
    """
    C1 = Cell(0, 400)
    C2 = Cell(0, 0)
    return [
        (C1, False),
        (C1, True),
        (C2, False),
        (C2, True),
    ]

def mantis_task(mantis: Mantis, path: list[tuple[Cell, bool, bool, int]], mqtt_client: MQTTClient, helper: Helper, loop_count: int):
    """
    线程任务：按路径循环执行拉/还箱动作序列，并通过 MQTT 下发复合指令。
    参数:
        mantis: 机器人实例
        path: 路径列表 [(Cell, load)]，load=True 为拉箱，False 为还箱
        mqtt_client: MQTT 客户端
        helper: 辅助工具（日志与回调）
        loop_count: 循环次数；-1 表示无限循环
    """
    if not path:
        return

    cnt = itertools.count(start=1, step=1)
    global FUXK_RUNNING
    i = 0

    while FUXK_RUNNING:
        # 如果是有限循环模式，超过次数就退出
        if loop_count != -1 and i >= loop_count:
            break

        helper.log_info("=" * 20 + f"test {next(cnt)}" + "=" * 20)
        for cell, load in path:
            mantis.state_update_flag = False
            while not mantis.state_update_flag:
                # 等待一次状态刷新，避免在旧状态基础上规划动作
                time.sleep(0.05)

            init_cell = Cell(mantis.position_x, mantis.position_z)
            target_x = cell.x
            target_z = cell.get_load_pos() if load else cell.get_unload_pos()
            helper.log_info(f"process move init_cell = {init_cell}, target_x = {target_x}, target_z = {target_z}...")

            if abs(init_cell.z - target_z) > 5:
                msg = build_mantis_move_command_set(
                    mantis.robot_label,
                    init_cell.x,
                    init_cell.z,
                    [[target_x, target_z, FULL_VEL_X, FULL_VEL_Z, FULL_ACC, FULL_ACC]]
                )
                mqtt_client.publish(
                    robot_label=mantis.robot_label,
                    topic=msg.topic,
                    payload=msg.payload
                )
                command_mantis = msg.payload["robotCommands"][-1]["robotCommandLabel"]
            else:
                command_mantis = None

            while (command_mantis and helper.complete_command[mantis.robot_label] != command_mantis):
                # 等待上一条位移命令完成
                time.sleep(0.05)

            if ENABLE_LHD:
                mantis.state_update_flag = False
                while not mantis.state_update_flag:
                    time.sleep(0.05)

            test_cases = test_cases_load if load else test_cases_unload
            commands = []
            last_arm_position = 0

            for test_case in test_cases:
                if test_case["type"] == "MOVE_ARMS":
                    tmp_msg = build_move_arms_command_set_simple(
                        robot_label=mantis.robot_label,
                        arm_position=test_case["arm_position"],
                        max_velocity=test_case["max_velocity"],
                        max_acceleration=test_case["max_acceleration"],
                        expect={
                            "armPosition": last_arm_position,
                            "armPositionTolerance": 10,
                            "loadSensors": test_case.get("expect", {}).get("loadSensors", {}),
                            "endOfArmSensors": test_case.get("expect", {}).get("endOfArmSensors", {})
                        },
                        future={
                            "armPosition": test_case["arm_position"],
                            "armPositionTolerance": 10,
                            "loadSensors": test_case.get("future", {}).get("loadSensors", {}),
                            "endOfArmSensors": test_case.get("future", {}).get("endOfArmSensors", {})
                        }
                    )
                    # print(f"[DEBUG] Sending MOVE_ARMS command: last_armPosition={last_arm_position}, armPosition={test_case['arm_position']}")
                    last_arm_position = test_case["arm_position"]
                elif test_case["type"] == "ARTICULATE_FINGERS":
                    tmp_msg = build_articulate_fingers_command_set_simple(
                        robot_label=mantis.robot_label,
                        pos=test_case["fingers"],
                        expect={
                            "armPosition": last_arm_position,
                            "armPositionTolerance": 10,
                            "toteGapSensors": {
                                # "frontLeft": False,"frontRight": False,
                                # "rearLeft": False,"rearRight": False,
                            },
                        },
                        future={
                            "fingerPosition": {
                                "left1": test_case["fingers"][0],
                                "right1": test_case["fingers"][4]
                            },
                            "fingerPositionTolerance": 300,
                            "toteGapSensors": {
                                # "frontLeft": False,"frontRight": False,
                                # "rearLeft": False,"rearRight": False,
                            },
                        }
                    )
                    
                commands.append(tmp_msg.payload["robotCommands"][0])

            msg = build_general_command_set_multiple(
                robot_label=mantis.robot_label,
                commands=commands
            )
            mqtt_client.publish(
                robot_label=mantis.robot_label,
                topic=msg.topic,
                payload=msg.payload
            )
            command_spyder = msg.payload["robotCommands"][-1]["robotCommandLabel"]

            while helper.complete_command[mantis.robot_label] != command_spyder:
                # 等待复合命令队列执行完成
                time.sleep(0.05)

        i += 1
        time1 = datetime.now()
        print(f"time: {time1}, round: {i}", flush=True)

def parse_args():
    """
    解析命令行参数：
    - -m/--mantis: 机器人标签（必填）
    - --server_ip/--server_port: MQTT 服务器地址与端口
    - --username/--password: MQTT 认证信息
    - -c/--count: 循环次数（-1 为无限循环，默认）
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mantis', required=True, help='Mantis robot label')
    parser.add_argument('--server_ip', default='10.0.7.136', help='MQTT server IP address (default: 10.0.7.136)')
    parser.add_argument('--server_port', type=int, default=1883, help='MQTT server port')
    parser.add_argument('--username', default='EE17G1eA', help='MQTT authentication username')
    parser.add_argument('--password', default='EE17G1eB', help='MQTT authentication password')
    parser.add_argument('-c', '--count', type=int, default=-1, help='循环次数，-1 为无限循环')
    return parser.parse_args()

def main(args):
    """
    主执行入口：初始化 MQTT 连接、构造工作线程、按回车停止并安全退出。
    """
    print(args)
    shelf_task = [(args.mantis, load_shelf_hz_path)]
    
    robot_list: list[Robot] = []
    work: list[tuple] = []
    
    for mantis_label, shelf_path_func in shelf_task:
        mantis = Mantis(mantis_label)
        robot_list.append(mantis)
        work.append((mantis, shelf_path_func()))
    
    helper = Helper(robot_list=robot_list, log_flag=MAIN_LOG)
    helper.log_info(args)
    
    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(
        host=args.server_ip,
        port=args.server_port,
        username=args.username,
        password=args.password
    )
    
    for robot in robot_list:
        mqtt_client.add_robot(robot.robot_label)
    
    try:
        while any([robot.state != "IDLE" for robot in robot_list]):
            time.sleep(1)
            
        thread_list = []
        global FUXK_RUNNING
        FUXK_RUNNING = True
        
        for w in work:
            if w and type(w[0]) is Mantis:
                mantis, path = w
                mantis_thread = threading.Thread(
                    target=mantis_task,
                    args=(mantis, path, mqtt_client, helper, args.count),  # 传循环次数
                    daemon=True
                )
                thread_list.append(mantis_thread)
                mantis_thread.start()
                
        input("press any key to stop...")
        FUXK_RUNNING = False
        
        while any(thread.is_alive() for thread in thread_list):
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        pass
    finally:
        mqtt_client.stop()
        print("fuxking done")

if __name__ == "__main__":
    main(parse_args())