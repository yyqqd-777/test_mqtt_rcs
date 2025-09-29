import canopen
import argparse
from spyder_drive import SpyderDrive


def main():
    parser = argparse.ArgumentParser(
        description='Current position of the flow motor read.')
    parser.add_argument(
        "flow_motor_pos", help="Initial position of the flow motor.", type=int)
    args = parser.parse_args()

    can_network = canopen.Network()
    can_network.connect(bustype='socketcan', channel='can0', bitrate=500000)

    spyder = SpyderDrive(can_network, args.flow_motor_pos)
    spyder.double_left_unload_action()


if __name__ == '__main__':
    main()
