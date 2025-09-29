import time
import canopen
import argparse
import sys
import signal
from dsr018_can import DSR018Can
from flow_motor import FlowMotor


def ds_motor_position_calculation(
    action: str, motor_id: int, distance_moved=1000
) -> int:
    """德晟电机目标位置计算

    Args:
        action (str): 拉箱: load, 还箱: unload
        motor_id (int): 电机id
        distance_moved (int, optional): 需要移动的距离. Defaults to 1000.

    Returns:
        int: 目标位置
    """
    if action == "load":
        if motor_id in [1, 4, 5, 8]:
            ret = 2100 + distance_moved
        elif motor_id in [2, 3, 6, 7]:
            ret = 2000 - distance_moved

    elif action == "unload":
        if motor_id in [1, 4, 5, 8]:
            ret = 2100
        elif motor_id in [2, 3, 6, 7]:
            ret = 2000

    else:
        return False

    return ret


def action(action, flow_motor, ds_motor_list):
    parameter = {"target_speed": 800000,
                 "acc": 300000, "dec": 300000, "claw_time": 200}

    fork_extension_dist = {
        "left_load": 640000,
        "left_unload": 645893,
        "right_load": -640000,
        "right_unload": -645893,
    }
    motor_ids = {
        "left_load": [3, 6, 4, 5],
        "left_unload": [3, 6, 4, 5],
        "right_load": [1, 2, 8, 7],
        "right_unload": [1, 2, 8, 7],
    }

    for ds_motor in ds_motor_list:
        if ds_motor['ds_motor_id'] in motor_ids[action]:
            if action == 'left_load' or action == 'right_load':
                ds_motor['ds_motor'].motor_action(
                    ds_motor['unload_position'], parameter['claw_time'])
            else:
                ds_motor['ds_motor'].motor_action(
                    ds_motor['load_position'], parameter['claw_time'])

    flow_pos = flow_motor.read_position_val()
    targe_position = flow_pos + fork_extension_dist[action]
    flow_motor.position_mode_run(
        targe_position, parameter["target_speed"], parameter["acc"], parameter["dec"]
    )

    while not flow_motor.check_pos_arrival():
        time.sleep(0.05)

    for ds_motor in ds_motor_list:
        if ds_motor["ds_motor_id"] in motor_ids[action]:
            if action == "left_load" or action == "right_load":
                ds_motor["ds_motor"].motor_action(
                    ds_motor["load_position"], parameter["claw_time"]
                )
            else:
                ds_motor["ds_motor"].motor_action(
                    ds_motor["unload_position"], parameter["claw_time"]
                )

    time.sleep(1)

    flow_motor.position_mode_run(
        flow_pos, parameter["target_speed"], parameter["acc"], parameter["dec"]
    )
    while not flow_motor.check_pos_arrival():
        time.sleep(0.05)


def main(args):
    print(args)

    ds_motor_list = []

    can_network = canopen.Network()
    can_network.connect(bustype="socketcan", channel="can0", bitrate=500000)
    can_network.nmt.state = "PRE-OPERATIONAL"

    flow_motor = FlowMotor(can_network, 9)

    flow_motor_init_pos = flow_motor.read_position_val(
    ) if not args.flow_motor_pos else args.flow_motor_pos
    flow_motor.position_mode_run(flow_motor_init_pos, 800000, 35000, 35000)

    for i in range(1, 9):
        motor_instance = DSR018Can(can_network, i)
        motor_dict = {
            "ds_motor": motor_instance,
            "ds_motor_id": i,
            "load_position": 0,
            "unload_position": 0,
        }
        ds_motor_list.append(motor_dict)

    for motor_dict in ds_motor_list:
        motor_dict["load_position"] = ds_motor_position_calculation(
            "load", motor_dict["ds_motor_id"], 1000
        )
        motor_dict["unload_position"] = ds_motor_position_calculation(
            "unload", motor_dict["ds_motor_id"]
        )

    time.sleep(1)

    can_network.nmt.state = "OPERATIONAL"

    action_name = args.action
    max_attempts = 3

    for i in range(max_attempts):
        try:
            action(action_name, flow_motor, ds_motor_list)
            break
        except:
            print("SDO timeout")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Current position of the flow motor read."
    )
    parser.add_argument(
        "-p",
        "--flow-motor-pos",
        type=int,
        default=0,
        help="Initial position of the flow motor.",
    )
    parser.add_argument(
        "-a",
        "--action",
        type=str,
        help="Action to be performed.",
    )
    return parser.parse_args()


def quit(signum, frame):
    print("stop test")
    sys.exit()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
    main(parse_args())
