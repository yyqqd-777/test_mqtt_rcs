import itertools
import threading
import time
import argparse
from helper import *

global FUXK_RUNNING
MAIN_LOG = True
ENABLE_LHD = False

FULL_VEL_X = 1500
FULL_VEL_Z = 1000
FULL_ACC = 500

test_cases_load = [
    {
        "type": "ARTICULATE_FINGERS",
        "fingers": [0, 0, 0, 0, 0, 0, 0, 0],
    },
    {
        "type": "MOVE_ARMS",
        "arm_position": -760,
        "max_velocity": 1000,
        "max_acceleration": 1000,
        "expect": {
            "loadSensors":{
                "frontInner": False,
                "frontOuter": False,
                "rearInner": False,
                "rearOuter": False,
            },
            "endOfArmSensors": {
                "rearRightInner": False,
                "rearRightOuter": False,
                "rearLeftInner": False,
                "rearLeftOuter": False,
            }
        },
        "future": {
            "endOfArmSensors": {
                "rearRightInner": False,
                "rearRightOuter": False,
                "rearLeftInner": False,
                "rearLeftOuter": False,
            }
        }
    },
    {
        "type": "ARTICULATE_FINGERS",
        "fingers": [9000, 0, 0, 0, 9000, 0, 0, 0],
    },
    {
        "type": "MOVE_ARMS",
        "arm_position": 20,
        "max_velocity": 800,
        "max_acceleration": 500,
        "expect": {
            "loadSensors":{
                "frontInner": False,
                "frontOuter": False,
                "rearInner": False,
                "rearOuter": False,
            },
        },
        "future": {
        }
    },
    {
        "type": "MOVE_ARMS",
        "arm_position": 0,
        "max_velocity": 1000,
        "max_acceleration": 1000,
        "expect": {
            "loadSensors":{
                "frontInner": True,
                "frontOuter": False,
                "rearInner": True,
                "rearOuter": True,
            },
        },
        "future": {
            "loadSensors":{
                "frontInner": True,
                "frontOuter": False,
                "rearInner": True,
                "rearOuter": True,
            },
        }
    },
    {
        "type": "ARTICULATE_FINGERS",
        "fingers": [0, 0, 0, 0, 0, 0, 0, 0],
    }
]

test_cases_unload = [
    {
        "type": "ARTICULATE_FINGERS",
        "fingers": [0, 0, 9000, 0, 0, 0, 9000, 0],
    },
    {
        "type": "MOVE_ARMS",
        "arm_position": -800,
        "max_velocity": 800,
        "max_acceleration": 500,
        "expect": {
            "loadSensors":{
                "frontInner": True,
                "frontOuter": False,
                "rearInner": True,
                "rearOuter": True,
            },
            "endOfArmSensors": {
                "rearRightOuter": False,
                "rearRightInner": False,
                "rearLeftInner": False,
                "rearLeftOuter": False,
            }
        },
        "future": {
            "loadSensors":{
                "frontInner": False,
                "frontOuter": False,
                "rearInner": False,
                "rearOuter": False,
            },
        }
    },
    {
        "type": "MOVE_ARMS",
        "arm_position": 0,
        "max_velocity": 1000,
        "max_acceleration": 1000,
        "expect": {
        },
        "future": {
        }
    },
    {
        "type": "ARTICULATE_FINGERS",
        "fingers": [0, 0, 0, 0, 0, 0, 0, 0],
    }
]

def load_shelf_hz_path() -> list[tuple[Cell, bool, bool, int]]:
    C1 = Cell(0, 0)
    C2 = Cell(0, 0)
    return [
        (C1, True),
        (C2, False),
        (C2, True),
        (C1, False),
    ]

def mantis_task(mantis: Mantis, path: list[tuple[Cell, bool, bool, int]], mqtt_client: MQTTClient, helper: Helper):
    if not path:
        return
    i = 0
    cnt = itertools.count(start=1, step=1)
    global FUXK_RUNNING
    while FUXK_RUNNING:
        helper.log_info("=" * 20 + f"test {next(cnt)}" + "=" * 20)
        for cell, load in path:
            mantis.state_update_flag = False
            while not mantis.state_update_flag:
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
                    last_arm_position = test_case["arm_position"]
                elif test_case["type"] == "ARTICULATE_FINGERS":
                    tmp_msg = build_articulate_fingers_command_set_simple(
                        robot_label=mantis.robot_label,
                        pos=test_case["fingers"],
                        expect={
                            "armPosition": last_arm_position,
                            "armPositionTolerance": 10,
                            "toteGapSensors": {
                                "frontLeft": False,
                                "frontRight": False,
                                "rearLeft": False,
                                "rearRight": False,
                            },
                        },
                        future={
                            "fingerPosition": {
                                "left1": test_case["fingers"][0],
                                "right1": test_case["fingers"][4]
                            },
                            "fingerPositionTolerance": 300,
                            "toteGapSensors": {
                                "frontLeft": False,
                                "frontRight": False,
                                "rearLeft": False,
                                "rearRight": False,
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
                time.sleep(0.05)
                
            i += 1
            time1 = datetime.now()
            print(f"time: {time1}, round: {i}", flush=True)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mantis', required=True, help='Mantis robot label')
    parser.add_argument('--server_ip', default='10.0.7.136', help='MQTT server IP address (default: 127.0.0.1)')
    parser.add_argument('--server_port', type=int, default=1883, help='MQTT server port')
    parser.add_argument('--username',default='EE17G1eA', help='MQTT authentication username')
    parser.add_argument('--password',default='EE17G1eB', help='MQTT authentication password')
    return parser.parse_args()

def main(args):
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
                    args=(mantis, path, mqtt_client, helper),
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