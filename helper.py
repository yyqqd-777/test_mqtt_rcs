import argparse
import collections
import math

from mqtt_service import *
from msg_generator_simple import *
from msg_generator import *
from robot import *

FULL_VEL = 2000
FULL_ACC = 500
FULL_DEC = 500


PD_LEVEL = -1770
C103_LEVEL = [
    -1016,
    -508,
    0,
    508,
    1016,
    1524,
    2032,
    2540,
    3150,
    3658,
    4166,
    4674,
    5182,
    5690,
    6198,
]

C103_COLUMN = [
    [0, 605, 1210, 1815],
    [2515, 3120, 3725, 4330],
    [5030, 5635],
    [7545, 8150, 8755, 9360],
    [10060, 10665, 11270, 11875],
    [12575, 13180, 13785, 14390],
    [15090, 15695, 16300, 16905],
    [17605, 18210, 18815, 19420],
    [20120, 20725],
    [22635, 23240, 23845, 24450],
    [25150, 25755, 26360, 26965],
    [27665, 28270, 28875, 29480],
]

FIRST_BAY = 0
C103_BAY = [
    2515,
    5030,
    7545,
    10060,
    12575,
    15090,
    17605,
    20120,
    22635,
    25150,
    27665,  # 30180
]

HZ_PD_LEVEL = 0
HZ_C002_LEVEL = [
    3000,
    1000,
    -100,
]


HZ_C002_BAY = [
    2000,
    5000,
    -2000,
]

HZ_C126_LEVEL = [
    2620,
]

HZ_C005_LEVEL = [
    540,
    540 + 525,
    540 + 525 * 2,
    540 + 525 * 3,
    540 + 525 * 4,
]

HZ_C005_BAY = [
    520,
    520 * 2,
    520 * 3,
    520 * 3 + 740,
    520 * 3 + 740 + 520 * 1,
    520 * 3 + 740 + 520 * 2,
    520 * 3 + 740 + 520 * 3,

]
HZ_CS006_BAY_test = [
    # [1440,610],
    [0,0],
    #[7000,2000],
    # [0,3500],
    # [1000, 4000],
    # [1500, 3000],
    # [3000, 5000],
    # [2000, 2000],
    # [2500, 1000],
]

HZ_CS006_BAY_2 = [
    
    [0, 0],
    # [1500, 3000],
    # [4000, 6000],
    # [2000, 2000],
    # [2500, 1000],
    # [0,0],
]
HZ_CS006_002MT = [
    # [2710,400],
    [0,3000],
    [0,500],
]

HZ_C136_01MT = [
    # [0,0],
    # [1185,25],
    [0,850],
]

HZ_2_01MT_Camera103 = [
    # [0,0],
    # [1185,25],
    [0,0],
]
HZ_CS006_003MT_T_ACC = [
    # [2500,6000],
    # [1000,3000],
    # [500,1500],
    # [200,6000],
    [0,0],
]
HZ_CS006_003MT = [
    # [2500,6000],
    [0,0],
    # [3400,30],
    # [2900,5180],    #震动
    # [3400,5180],
    # [2900,3580],  #3580箱位不可用
    # [3400,3580],  #震动测试
    # [2900,430],   #震动测试
    # [3400,430],   #震动测试
    # [190,30],     #0位
    # [190,780],    #3层
    # [690,780],
    # [1190,780],
    # [2900,3580],
    # [3400,780],
    # [1000, 4000],
    # [1500, 3000],
    # [3000, 5000],
    # [2000, 2000],
    # [2500, 1000],
]

HZ_C1308_BAY_1 = [
    [0,400],
    # [1000, 4000],
    # [1500, 3000],
    # [3000, 5000],
    # [2000, 2000],
    # [2500, 1000],
]

class Cell:
    offset = 0
    diff = 10

    def __init__(self, x: int, z: int):
        self.x = x
        self.z = z

    def __repr__(self):
        return f"Cell({self.x}, {self.z})"

    def get_load_pos(self):
        return self.z + self.offset - self.diff

    def get_unload_pos(self):
        return self.z + self.offset + self.diff


class Node:
    def __init__(self, x: int, y: int, ori: float = 180, lift: int = 0):
        self.x = x
        self.y = y
        self.ori = ori
        self.lift = lift

    def __repr__(self):
        return f"x: {self.x}, y: {self.y}, ori: {self.ori}, lift: {self.lift}"

    def get_state(self):
        return self.x, self.y, self.ori, self.lift


def parse_args():
    parser = argparse.ArgumentParser(description="new-pick-s test arguments")
    parser.add_argument(
        "-i",
        "--server-ip",
        type=str,
        # default="39.185.88.181", #4g
        default="10.0.7.136",
        help="MQTT broker ip, default = 10.0.7.136",
    )
    parser.add_argument(
        "-p",
        "--server-port",
        type=int,
        # default=58883, #4g
        default=1883,
        help="MQTT broker port, default = 1883",
    )
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        default='EE17G1eA',
        help="MQTT client username, default = 'EE17G1eA'",
    )
    parser.add_argument(
        "-w",
        "--password",
        type=str,
        default='EE17G1eB',
        help="MQTT client password, default = 'EE17G1eB'",
    )
    parser.add_argument(
        "-g",
        "--general",
        type=str,
        default="UNKNOWN",
        help="robot's label, default = 'UNKNOWN'",
    )
    parser.add_argument(
        "-a",
        "--ant",
        type=str,
        default='UNKNOWN',
        help="ant's label, default = 'UNKNOWN'",
    )
    parser.add_argument(
        "-l",
        "--ladder",
        type=str,
        default='UNKNOWN',
        help="ladder's label, default = 'UNKNOWN'",
    )
    parser.add_argument(
        "-s",
        "--spyder",
        type=str,
        default='UNKNOWN',
        help="spyder's label, default = 'UNKNOWN'",
    )
    parser.add_argument(
        "-m",
        "--mantis",
        type=str,
        default='UNKNOWN',
        help="mantis's label, default = 'UNKNOWN'",
    )
    parser.add_argument(
        "-x",
        "--origin-x",
        type=int,
        default='0',
        help="ladder's or spyder's origin coord, default = 0",
    )
    parser.add_argument(
        "-c",
        "--cycle-count",
        type=int,
        default=1,
        help="cycle task count",
    )
    return parser.parse_args()


def calculate_angle(x1, y1, x2, y2):
    # Calculate the differences
    delta_x = x2 - x1
    delta_y = y2 - y1

    # Calculate the angle in radians
    theta_radians = math.atan2(delta_y, delta_x)

    # Convert angle to degrees
    theta_degrees = math.degrees(theta_radians)

    # Normalize the angle to be within 0 to 360 degrees
    if theta_degrees < 0:
        theta_degrees += 360

    return theta_degrees


def find_path(start: Node, end: Node) -> list[list]:
    path = []

    if abs(start.x - end.x) > 50 or abs(start.y - end.y) > 50:
        # 计算start - end行走路径的角度，结果范围为[0, 360)
        angle = calculate_angle(start.x, start.y, end.x, end.y)

        # 某些情况下，end点位对机器人角度有特定要求，比如：充电桩需要倒退进入，接驳位需要正向进入
        # 通过定义end点位的orientation，来进行限制
        # 当行进方向与限制方向正好相反时，优先以限制方向进行移动
        if abs(abs(angle - end.ori) - 180) <= 5:
            angle = end.ori

        # 当angle与start点位方向接近时，也无需旋转
        if abs(angle - start.ori) > 5:
            path.append(['SPIN', angle])

        path.append(['MOVE', end.x, end.y, FULL_VEL, FULL_ACC, FULL_DEC])

    # 当end点位的高度与start点位的高度不同时，需要进行高度调整
    if start.lift != end.lift:
        path.append(["LIFT", end.lift])
    return path


def find_full_path(node_list: list[Node]) -> list[list]:
    FULL_VEL = 2000
    FULL_ACC = 500

    path = []

    n = len(node_list)
    for i in range(n - 1):
        start, end = node_list[i], node_list[i + 1]

        if abs(start.x - end.x) > 50 or abs(start.y - end.y) > 50:
            # 计算start - end行走路径的角度，结果范围为[0, 360)
            angle = calculate_angle(start.x, start.y, end.x, end.y)

            # 某些情况下，end点位对机器人角度有特定要求，比如：充电桩需要倒退进入，接驳位需要正向进入
            # 通过定义end点位的orientation，来进行限制
            # 当行进方向与限制方向正好相反时，优先以限制方向进行移动
            if abs(abs(angle - end.ori) - 180) <= 5:
                angle = end.ori

            # 当angle与start点位方向接近时，也无需旋转
            if abs(angle - start.ori) > 5:
                path.append(['SPIN', angle])

            path.append(['MOVE', end.x, end.y, FULL_VEL, FULL_ACC])

            # 更新end点位方向，供后续路径规划
            node_list[i + 1].ori = angle
        else:
            # 当start点位与end点位重合时，无需旋转及行走
            node_list[i + 1].ori = start.ori

        # 当end点位的高度与start点位的高度不同时，需要进行高度调整
        if start.lift != end.lift:
            path.append(['LIFT', end.lift])

    return path


def test_pair_generator_unused(nodes: list[Node]):
    commands = []
    for start, end in zip(nodes, nodes[1:]):
        commands += find_path(start, end)
    return commands


class Helper:
    robot_list: list[Robot]
    last_complete_command_label = "UNKNOWN"
    complete_command = collections.defaultdict(str)

    def __init__(self, robot_list: list[Robot], log_flag=False):
        self.robot_list = robot_list
        self.log = LogTool("helper", "helper.log").get_logger()
        self.log_flag = log_flag

    def log_info(self, msg):
        if self.log_flag:
            self.log.info(msg)
        else:
            print(msg)

    @ staticmethod
    def is_robot_state(robot: Robot, topic: str):
        return f"robot/state/{robot.robot_label}" == topic

    @ staticmethod
    def is_robot_command_state(robot: Robot, topic: str):
        return f"robot/command/status/{robot.robot_label}" == topic

    @ staticmethod
    def is_robot_command_set(robot: Robot, topic: str):
        return f"robot/commandSet/create/{robot.robot_label}" == topic

    def mqtt_receive_callback(self, message: MQTTMsg):
        topic, payload = message.topic, json.loads(message.payload)
        for r in self.robot_list:
            if self.is_robot_state(r, topic):
                r.update_state(payload)
                r.state_update_flag = True
                self.log.info(r)
            if self.is_robot_command_state(r, topic):
                if payload["status"] == "COMPLETE_SUCCESS":
                    self.last_complete_command_label = payload["robotCommandLabel"]
                    self.complete_command[r.robot_label] = payload["robotCommandLabel"]
                    self.log.info(
                        f"{r.robot_type} {r.robot_label} WORKING ==> "
                        f"{payload['robotCommandLabel']} {payload['status']}"
                    )
