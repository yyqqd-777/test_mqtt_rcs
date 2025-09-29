class Robot(object):
    """
    机器人类，用于保存机器人的状态
    """
    state_update_flag = False
    state = "None"

    def __init__(self, robot_type, robot_label):
        self.robot_type = robot_type
        self.robot_label = robot_label

    def __str__(self) -> str:
        print(self.robot_label, self.robot_type, self.state)
        return "type: {:<7} id: {:<10} state: {:<15}".format(
            self.robot_type, self.robot_label, self.state
        )

    def update_state(self, payload):
        self.state = payload["mainState"]


class Ant(Robot):
    """
    蚂蚁机器人类
    """
    position_x: int
    position_y: int
    orientation: int
    scan_state: str | bool = "Unknown"
    battery: int

    def __init__(self, robot_label, drop_height=0, lift_height=100):
        super().__init__("ANT", robot_label)
        self.height = self.drop_height = drop_height
        self.lift_height = lift_height

    def __str__(self) -> str:
        return (
            "type: {:<7} id: {:<10} state: {:<15} "
            "x: {:<7} y: {:<7} ori: {:<7} "
            "height: {:<5} scan: {:<5} bat: {:<3}%".format(
                self.robot_type,
                self.robot_label,
                self.state,
                self.position_x,
                self.position_y,
                self.orientation,
                self.height,
                self.scan_state,
                self.battery
            )
        )

    def is_lifted(self):
        return abs(self.height - self.lift_height) < 5

    def is_dropped(self):
        return abs(self.height - self.drop_height) < 5

    def update_state(self, payload):
        self.state = payload["mainState"]
        self.position_x = payload["coordX"]
        self.position_y = payload["coordY"]
        self.orientation = payload["orientation"]
        self.scan_state = payload["qrCodeStatus"]
        self.height = payload["liftHeight"]
        self.battery = payload["batPct"]


class Mole(Robot):
    """
    鼹鼠机器人类
    """

    load_state: str | bool

    def __init__(self, robot_label):
        super().__init__("MOLE", robot_label)

    def is_loaded(self):
        return self.load_state == 1

    def is_empty(self):
        return self.load_state == 0

    def update_state(self, payload):
        self.state = payload["mainState"]
        self.load_state = payload["loaded"] if "loaded" in payload else "Unknown"


class Spyder(Robot):
    """
    蜘蛛机器人类
    """
    position: int
    scan_state: str | bool = "Unknown"
    scan_data: str
    scan_x: int
    scan_z: int
    load_sensor_front: bool
    load_sensor_rear: bool
    antipinch_sensor_front: bool
    antipinch_sensor_rear: bool

    def __init__(self, robot_label):
        super().__init__("SPYDER", robot_label)

    def __str__(self) -> str:
        return (
            "type: {:<7} id: {:<10} state: {:<15} z: {:<7} "
            "scan: {:<4} data: {:<20} x_off: {:<4} z_off: {:<4}".format(
                self.robot_type,
                self.robot_label,
                self.state,
                self.position,
                self.scan_state,
                self.scan_data,
                self.scan_x,
                self.scan_z,
            )
        )

    def is_scanned(self):
        return self.scan_state

    def is_dm_code(self):
        return self.scan_state and len(self.scan_data) == 16 and self.scan_data.isdigit()

    def update_state(self, payload):
        self.state = payload["mainState"]
        self.position = payload["coordZ"]
        self.scan_state = payload["scannerStatus"]["qrCodeStatus"]
        self.scan_data = payload["scannerStatus"]["scannerData"]
        self.scan_x = payload["scannerStatus"]["scannerCoordX"]
        self.scan_z = payload["scannerStatus"]["scannerCoordZ"]
        self.load_sensor_front = payload["sensorStatus"]["loadSensorFront"]
        self.load_sensor_rear = payload["sensorStatus"]["loadSensorRear"]
        self.antipinch_sensor_front = payload["sensorStatus"]["antipinchSensorFront"]
        self.antipinch_sensor_rear = payload["sensorStatus"]["antipinchSensorRear"]


class Ladder(Robot):
    """
    梯子机器人类
    """
    position: int

    def __init__(self, robot_label):
        super().__init__("LADDER", robot_label)

    def __str__(self) -> str:
        return (
            "type: {:<7} id: {:<10} state: {:<15} x: {:<7}".format(
                self.robot_type,
                self.robot_label,
                self.state,
                self.position
            )
        )

    def update_state(self, payload):
        self.state = payload["mainState"]
        self.position = payload["coordX"]


class Mantis(Robot):
    """
    螳螂机器人类
    """
    position_x: int
    position_z: int
    scan_state: str | bool = "Unknown"
    scan_data: str
    scan_x: int
    scan_z: int
    load_sensor_front: bool
    load_sensor_rear: bool
    antipinch_sensor_front: bool
    antipinch_sensor_rear: bool

    def __init__(self, robot_label):
        super().__init__("LADDER_SPYDER", robot_label)

    def __str__(self) -> str:
        return (
            "type: {:<7} id: {:<10} state: {:<15} x: {:<7} z: {:<7} "
            "scan: {:<4} data: {:<20} x_off: {:<4} z_off: {:<4}".format(
                self.robot_type,
                self.robot_label,
                self.state,
                self.position_x,
                self.position_z,
                self.scan_state,
                self.scan_data,
                self.scan_x,
                self.scan_z,
            )
        )

    def is_scanned(self):
        return self.scan_state

    def is_dm_code(self):
        return self.scan_state and len(self.scan_data) == 16 and self.scan_data.isdigit()

    def update_state(self, payload):
        self.state = payload["mainState"]
        self.position_x = payload["coordX"]
        self.position_z = payload["coordZ"]
        self.scan_state = payload["scannerStatus"]["qrCodeStatus"]
        self.scan_data = payload["scannerStatus"]["scannerData"]
        self.scan_x = payload["scannerStatus"]["scannerCoordX"]
        self.scan_z = payload["scannerStatus"]["scannerCoordZ"]
