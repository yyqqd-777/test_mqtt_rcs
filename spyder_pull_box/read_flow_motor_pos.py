import canopen
import argparse
from flow_motor import FlowMotor

parser = argparse.ArgumentParser(description='Current position of the flow motor read.')
parser.add_argument("motor_id", help="canid of the flow motor.", type = int)
args = parser.parse_args()

can_network = canopen.Network()
can_network.connect(bustype='socketcan', channel='can0', bitrate=500000)

flow_motor = FlowMotor(can_network, args.motor_id)

flow_pos = flow_motor.read_position_val()
print(f'Current position of the flow motor: {flow_pos}')
