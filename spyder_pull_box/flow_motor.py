import canopen


class FlowMotor:
    target_position: int

    def __init__(self, can_network, node_id):
        self.node = can_network.add_node(node_id, 'flowservo.eds')
        self.node.sdo.RESPONSE_TIMEOUT = 1.5

    def position_mode_run(self, position: int, speed: int, acceleration: int, deceleration: int):
        """_summary_

        Args:
            position (int): target position
            speed (int): target speed
            acceleration (int): target acceleration
            deceleration (int): target deceleration
        """
        self.target_position = position
        self.node.sdo.download(0x6060, 0, b'\x01')
        self.node.sdo.download(0x607A, 0, position.to_bytes(
            4, byteorder='little', signed=True))
        self.node.sdo.download(
            0x6081, 0, speed.to_bytes(4, byteorder='little'))
        self.node.sdo.download(
            0x6083, 0, acceleration.to_bytes(4, byteorder='little'))
        self.node.sdo.download(
            0x6084, 0, deceleration.to_bytes(4, byteorder='little'))
        self.node.sdo.download(0x6040, 0, b'\x80\x00')
        self.node.sdo.download(0x6040, 0, b'\x00\x00')
        self.node.sdo.download(0x6040, 0, b'\x06\x00')
        self.node.sdo.download(0x6040, 0, b'\x07\x00')
        self.node.sdo.download(0x6040, 0, b'\x0F\x00')
        self.node.sdo.download(0x6040, 0, b'\x2F\x00')
        self.node.sdo.download(0x6040, 0, b'\x3F\x00')

    def read_position_val(self):
        val = self.node.sdo[0x6064].raw
        return val

    def read_statusword_val(self):
        val = self.node.sdo[0x6041].raw
        return val

    def check_pos_arrival(self):
        if (self.read_statusword_val() & 0x400) and abs(self.read_position_val() - self.target_position) < 100:
            return True
        else:
            return False
