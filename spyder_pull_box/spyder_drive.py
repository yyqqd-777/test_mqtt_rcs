import time
from dsr018_motor import DSR018Can
from flow_motor import FlowMotor

FLOW_MOTOR_WAIT_INTERVAL = 0.01


class SpyderDrive:
    def __init__(self, can_network, init_pos_flow_motor):
        self.can_network = can_network

        self.fork_running_config = {
            'profile acc': 500,  # 轮廓加速度
            'profile dec': 500,  # 轮廓减速度
            'profile speed': 1000,  # 轮廓速度
        }

        self.box_distances_config = {
            "single deep pull box": 764 + 40,  # 单深拉箱子货叉伸出的距离
            "single deep return box": 824 + 20,  # 单深还箱子货叉伸出的距离
            "double deep pull box": 1410,  # 双深拉箱子货叉伸出的距离
            "double deep return box": 1470  # 双深还箱子货叉伸出的距离
        }

        self.reduction_ratio_config = {
            'subdivisions': 10000,
            'reduction ratio': 15,
            'gear teeth': 34 * 2,
            'gear pitch': 5,
            'result': 0
        }

        self.fork_running_subdivision = {
            'profile acc': 0,
            'profile dec': 0,
            'profile speed': 0,
        }

        self.box_distances_subdivision = {
            "single deep pull box": 0,
            "single deep return box": 0,
            "double deep pull box": 0,
            "double deep return box": 0
        }

        self.ds_motor_list = []
        self.init_pos_flow_motor = init_pos_flow_motor

        self.motor_init()

    def motor_init(self):
        # 计算货叉伸臂距离减速比系数
        self.reduction_ratio_config['result'] = self.calculate_reduction_ratio(
            self.reduction_ratio_config['subdivisions'],
            self.reduction_ratio_config['reduction ratio'],
            self.reduction_ratio_config['gear teeth'],
            self.reduction_ratio_config['gear pitch']
        )

        # 换算加减速的细分值
        for k, v in self.fork_running_subdivision.items():
            self.fork_running_subdivision[k] = self.reduction_ratio_config['result'] * \
                self.fork_running_config[k]

        # 换算货叉移动距离的细分值
        for k, v in self.box_distances_subdivision.items():
            self.box_distances_subdivision[k] = self.reduction_ratio_config['result'] * \
                self.box_distances_config[k]

        self.parameter = {
            'claw_time': 200
        }

        self.fork_extension_dist = {
            'left load': self.box_distances_subdivision['single deep pull box'],
            'left unload': self.box_distances_subdivision['single deep return box'],
            'right load': -1 * self.box_distances_subdivision['single deep pull box'],
            'right unload': -1 * self.box_distances_subdivision['single deep return box'],
            'double left load': self.box_distances_subdivision['double deep pull box'],
            'double left unload': self.box_distances_subdivision['double deep return box'],
            'double right load': -1 * self.box_distances_subdivision['double deep pull box'],
            'double right unload': -1 * self.box_distances_subdivision['double deep return box']

        }

        self.motor_ids = {
            'left load': [3, 4],
            'left unload': [6, 5],
            'right load': [1, 2],
            'right unload': [8, 7],
            'double left load': [3, 4],
            'double left unload': [6, 5],
            'double right load': [1, 2],
            'double right unload': [8, 7],
        }

        # 初始化canopen网络
        self.can_network.nmt.state = 'PRE-OPERATIONAL'

        # 初始化德晟电机
        for i in range(1, 9):
            motor_instance = DSR018Can(self.can_network, i)
            load_position = self.ds_motor_position_calculation(
                action='load', motor_id=i)
            unload_position = self.ds_motor_position_calculation(
                action='unload', motor_id=i)
            motor_dict = {
                "ds_motor": motor_instance,
                "ds_motor_id": i,
                "load_position": load_position,
                "unload_position": unload_position,
            }
            self.ds_motor_list.append(motor_dict)

        for motor_dict in self.ds_motor_list:
            motor_dict['ds_motor'].motor_action(
                motor_dict['unload_position'], 200)
        time.sleep(self.parameter['claw_time'] / 1000)

        # 初始化心流电机
        self.flow_motor = FlowMotor(can_network=self.can_network, node_id=9)
        self.flow_motor.position_mode_run(position=self.init_pos_flow_motor,
                                          speed=self.fork_running_subdivision['profile speed'],
                                          acceleration=self.fork_running_subdivision['profile acc'],
                                          deceleration=self.fork_running_subdivision['profile dec'])
        while not self.flow_motor.check_pos_arrival():
            time.sleep(FLOW_MOTOR_WAIT_INTERVAL)

        self.can_network.nmt.state = 'OPERATIONAL'

    def load_action(self, action_str: str):
        """拉箱子动作

        Args:
            action_str: 要执行的具体动作
                'left load'
                'right load'
                'double left load'
                'double right load'

        Returns: None

        """
        # 叉臂伸出去
        flow_pos = self.flow_motor.read_position_val()
        targe_position = flow_pos + self.fork_extension_dist[action_str]
        self.flow_motor.position_mode_run(position=targe_position,
                                          speed=self.fork_running_subdivision['profile speed'],
                                          acceleration=self.fork_running_subdivision['profile acc'],
                                          deceleration=self.fork_running_subdivision['profile dec'])
        while not self.flow_motor.check_pos_arrival():
            time.sleep(FLOW_MOTOR_WAIT_INTERVAL)

        # 指定的爪子落下去
        for ds_motor in self.ds_motor_list:
            if ds_motor['ds_motor_id'] in self.motor_ids[action_str]:
                ds_motor['ds_motor'].motor_action(
                    ds_motor['load_position'], self.parameter['claw_time'])
            else:
                ds_motor['ds_motor'].motor_action(
                    ds_motor['unload_position'], self.parameter['claw_time'])
        time.sleep(self.parameter['claw_time'] / 1000)

        # 叉臂缩回来
        self.flow_motor.position_mode_run(position=flow_pos,
                                          speed=self.fork_running_subdivision['profile speed'],
                                          acceleration=self.fork_running_subdivision['profile acc'],
                                          deceleration=self.fork_running_subdivision['profile dec'])
        while not self.flow_motor.check_pos_arrival():
            time.sleep(FLOW_MOTOR_WAIT_INTERVAL)

        # 爪子全部升起
        for ds_motor in self.ds_motor_list:
            ds_motor['ds_motor'].motor_action(
                ds_motor['unload_position'], self.parameter['claw_time'])
        time.sleep(self.parameter['claw_time'] / 1000)

    def unload_action(self, action_str: str):
        """还箱子动作

        Args:
            action_str: 要执行的具体动作
                'left unload'
                'right unload'
                'double left unload'
                'double right unload'

        Returns:None

        """
        # 指定的爪子落下去
        for ds_motor in self.ds_motor_list:
            if ds_motor['ds_motor_id'] in self.motor_ids[action_str]:
                ds_motor['ds_motor'].motor_action(
                    ds_motor['load_position'], self.parameter['claw_time'])
            else:
                ds_motor['ds_motor'].motor_action(
                    ds_motor['unload_position'], self.parameter['claw_time'])
        time.sleep(self.parameter['claw_time'] / 1000)

        # 叉臂伸出去
        flow_pos = self.flow_motor.read_position_val()
        targe_position = flow_pos + self.fork_extension_dist[action_str]
        self.flow_motor.position_mode_run(position=targe_position,
                                          speed=self.fork_running_subdivision['profile speed'],
                                          acceleration=self.fork_running_subdivision['profile acc'],
                                          deceleration=self.fork_running_subdivision['profile dec'])
        while not self.flow_motor.check_pos_arrival():
            time.sleep(FLOW_MOTOR_WAIT_INTERVAL)

        # 爪子全部升起
        for ds_motor in self.ds_motor_list:
            ds_motor['ds_motor'].motor_action(
                ds_motor['unload_position'], self.parameter['claw_time'])
        time.sleep(self.parameter['claw_time'] / 1000)

        # 叉臂缩回来
        self.flow_motor.position_mode_run(position=flow_pos,
                                          speed=self.fork_running_subdivision['profile speed'],
                                          acceleration=self.fork_running_subdivision['profile acc'],
                                          deceleration=self.fork_running_subdivision['profile dec'])
        while not self.flow_motor.check_pos_arrival():
            time.sleep(FLOW_MOTOR_WAIT_INTERVAL)

    def left_load_action(self):
        self.load_action('left load')

    def left_unload_action(self):
        self.unload_action('left unload')

    def right_load_action(self):
        self.load_action('right load')

    def right_unload_action(self):
        self.unload_action('right unload')

    def double_left_load_action(self):
        self.load_action('double left load')

    def double_left_unload_action(self):
        self.unload_action('double left unload')

    def double_right_load_action(self):
        self.load_action('double right load')

    def double_right_unload_action(self):
        self.unload_action('double right unload')

    def calculate_reduction_ratio(self, subdivisions, reduction_ratio, gear_teeth, gear_pitch):
        """计算货叉伸臂距离减速比系数（1 / 齿数 / 齿距 * 减速比 * 细分）

        Args:
            subdivisions: 电机旋转一圈的细分
            reduction_ratio: 减速比
            gear_teeth: 齿轮齿数
            gear_pitch: 齿轮齿距

        Returns:
            减速比系数，单位mm
            移动距离（mm）* 系数 = 要下发的细分


        """
        total_subdivisions = subdivisions * reduction_ratio
        gear_circumference = gear_teeth * gear_pitch
        reduction_coefficient = total_subdivisions / gear_circumference
        return round(reduction_coefficient)

    def ds_motor_position_calculation(self, action: str, motor_id: int, distance_moved=1000) -> int:
        """德晟电机目标位置计算

        Args:
            action (str): 拉箱: load, 还箱: unload
            motor_id (int): 电机id
            distance_moved (int, optional): 需要移动的距离. Defaults to 1000.

        Returns:
            int: 目标位置
        """
        if action == 'load':
            if motor_id in [1, 4, 5, 8]:
                ret = 2100 + distance_moved
            elif motor_id in [2, 3, 6, 7]:
                ret = 2000 - distance_moved
            else:
                ret = 0
        elif action == 'unload':
            if motor_id in [1, 4, 5, 8]:
                ret = 2100
            elif motor_id in [2, 3, 6, 7]:
                ret = 2000
            else:
                ret = 0
        else:
            return False

        return ret
