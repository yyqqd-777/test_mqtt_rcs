from datetime import datetime
from mqtt_service import MQTTMsg


def build_ladder_move_command(
        robot_label: str,
        set_id: str,
        command_id: str | int,
        init_position: int,
        target_position: int,
        vel: int,
        acc: int
):
    return {
        "robotCommandLabel": f"{robot_label}-{set_id}-{command_id}",
        "previousCommandLabel": f"",
        "commandContent": {
            "robotCommandType": "MOVE",
            "coordX": target_position,
            "maxVelocity": vel,
            "maxAcceleration": acc,
        },
        "expectedState": {
            "coordX": init_position,
            "xTolerance": 10,
            "velocity": 0,
            "velocityTolerance": 50,
            "acceleration": 0,
            "accelerationTolerance": 50,
        },
        "futureState": {
            "coordX": target_position,
            "xTolerance": 10,
            "velocity": 0,
            "velocityTolerance": 50,
            "acceleration": 0,
            "accelerationTolerance": 50,
        },
    }


def build_mantis_move_command(
        robot_label: str,
        set_id: str,
        command_id: str | int,
        init_position_x: int,
        init_position_z: int,
        target_position_x: int,
        target_position_z: int,
        vel_x: int,
        vel_z: int,
        acc_x: int,
        acc_z: int,
        sCurve_profile: bool = False
):
    return {
        "robotCommandLabel": f"{robot_label}-{set_id}-{command_id}",
        "previousCommandLabel": f"",
        "commandContent": {
            "robotCommandType": "MOVE",
            "coordX": target_position_x,
            "coordZ": target_position_z,
            "maxVelocityX": vel_x,
            "maxVelocityZ": vel_z,
            "maxAccelerationX": acc_x,
            "maxAccelerationZ": acc_z,
            "sCurveProfile": sCurve_profile,
            "maxJerkX": 200,   #加加速
            "maxJerkZ": 200,   #加减速
        },
        "expectedState": {
            "coordX": init_position_x,
            "coordZ": init_position_z,
            "xTolerance": 10,
            "zTolerance": 10,
            "velocityX": 0,
            "velocityXTolerance": 50,
            "velocityZ": 0,
            "velocityZTolerance": 30000,
            "antiPinchSensors":{
                "front": False,
                "rear": False,
                # "Left": False,
                # "Right": False
            },          
            # "loadSensors":{
            #     "frontInner": False,
            #     "frontOuter": False,
            #     "rearInner": False,
            #     "rearOuter": False,
            # },
            # "toteGapSensors":{
            #     "frontLeft": False,
            #     "frontRight": False,
            #     "rearLeft": False,
            #     "rearRight": False,
            # },
            # "endOfArmSensors": {
            #     "rearRightInner": False,
            #     "rearRightOuter": False,
            #     "rearLeftInner": False,
            #     "rearLeftOuter": False,
            #     "frontRightInner": False,
            #     "frontRightOuter": False,
            #     "frontLeftInner": False,
            #     "frontLeftOuter": False
            # }
        },
        "futureState": {
            "coordX": target_position_x,
            "coordZ": target_position_z,
            "xTolerance": 10,
            "zTolerance": 10,
            "velocityX": 0,
            "velocityXTolerance": 50,
            "velocityZ": 0,
            "velocityZTolerance": 30000,
            "antiPinchSensors":{
                "front": False,
                "rear": False,
                # "Left": False,
                # "Right": False
            },          
            # "loadSensors":{
            #     "frontInner": False,
            #     "frontOuter": False,
            #     "rearInner": False,
            #     "rearOuter": False,
            # },
            # "toteGapSensors":{
            #     # "front": False,
            #     # "rear": False,
            #     "frontInner": False,
            #     "frontOuter": False,
            #     "rearInner": False,
            #     "rearOuter": False,
            # },
            # "endOfArmSensors": {
                # "rearRightInner": False,
                # "rearRightOuter": False,
                # "rearLeftInner": False,
                # "rearLeftOuter": False,
            #     "frontRightInner": False,
            #     "frontRightOuter": False,
            #     "frontLeftInner": False,
            #     "frontLeftOuter": False
            # }
    }
    }

def build_mantis_move_command_set(robot_label: str, init_pos_x: int, init_pos_z: int, command_param: list):
    topic = f"robot/commandSet/create/{robot_label}"
    set_id = f"SET-{datetime.now().isoformat()}"

    commands = []
    for command_id, (target_pos_x, target_pos_z, vel_x, vel_z, acc_x, acc_z) in enumerate(command_param):
        commands.append(build_mantis_move_command(
            robot_label, set_id, str(command_id + 1), init_pos_x, init_pos_z, target_pos_x, target_pos_z, vel_x, vel_z, acc_x, acc_z))
        init_pos_x = target_pos_x
        init_pos_z = target_pos_z

    payload = {
        "robotCommandSetLabel": f"{robot_label}-{set_id}",
        "timestamp": datetime.now().isoformat(),
        "robotCommands": commands,
    }
    return MQTTMsg(topic, payload)


def build_ladder_move_command_set(robot_label: str, init_pos: int, command_param: list):
    topic = f"robot/commandSet/create/{robot_label}"
    set_id = f"SET-{datetime.now().isoformat()}"

    commands = []
    for command_id, (target_pos, vel, acc) in enumerate(command_param):
        commands.append(build_ladder_move_command(
            robot_label, set_id, str(command_id + 1), init_pos, target_pos, vel, acc))
        init_pos = target_pos

    payload = {
        "robotCommandSetLabel": f"{robot_label}-{set_id}",
        "timestamp": datetime.now().isoformat(),
        "robotCommands": commands,
    }
    return MQTTMsg(topic, payload)


def build_ladder_home_command_set(
        robot_label: str,
        command_type: str,
        distance_between_dm_codes: int = 0,
        distance_to_adjust: int = 0,
        origin_offset: int = 0
):
    topic = f"robot/commandSet/create/{robot_label}"
    set_id = f"SET-{datetime.now().isoformat()}"

    commands = [
        {
            "robotCommandLabel": f"{robot_label}-{set_id}-0",
            "previousCommandLabel": f"",
            "commandContent": {
                "robotCommandType": command_type,
                "distanceBetweenDmCodes": distance_between_dm_codes,
                "distanceToAdjust": distance_to_adjust,
                "originOffset": origin_offset
            },
            "expectedState": {
                "coordX": 0,
                "xTolerance": 10,
                "velocity": 0,
                "velocityTolerance": 50,
                "acceleration": 0,
                "accelerationTolerance": 50
            },
            "futureState": {
                "coordX": 0,
                "xTolerance": 10,
                "velocity": 0,
                "velocityTolerance": 50,
                "acceleration": 0,
                "accelerationTolerance": 50
            }
        }
    ]

    payload = {
        "robotCommandSetLabel": f"{robot_label}-{set_id}",
        "timestamp": datetime.now().isoformat(),
        "robotCommands": commands,
    }
    return MQTTMsg(topic, payload)


def build_mantis_home_command_set(
        robot_label: str,
        command_type: str,
        distance_between_dm_codes: int = 0,
        distance_to_dm_codes: int = 0,
        distance_to_adjust: int = 0,
        origin_offset_x: int = 0,
        origin_offset_z: int = 0
):
    topic = f"robot/commandSet/create/{robot_label}"
    set_id = f"SET-{datetime.now().isoformat()}"

    commands = [
        {
            "robotCommandLabel": f"{robot_label}-{set_id}-0",
            "previousCommandLabel": f"",
            "commandContent": {
                "robotCommandType": command_type,
                "distanceBetweenDmCodes": distance_between_dm_codes,
                "distanceToDmCodes": distance_to_dm_codes,
                "distanceToAdjust": distance_to_adjust,
                "originOffsetX": origin_offset_x,
                "originOffsetZ": origin_offset_z
            },
            "expectedState": {
                "coordX": 0,
                "coordZ": 0,
                "xTolerance": 10,
                "zTolerance": 10,
                "velocity": 0,
                "velocityTolerance": 50,
                "acceleration": 0,
                "accelerationTolerance": 50
            },
            "futureState": {
                "coordX": 0,
                "coordZ": 0,
                "xTolerance": 10,
                "zTolerance": 10,
                "velocity": 0,
                "velocityTolerance": 50,
                "acceleration": 0,
                "accelerationTolerance": 50
            }
        }
    ]

    payload = {
        "robotCommandSetLabel": f"{robot_label}-{set_id}",
        "timestamp": datetime.now().isoformat(),
        "robotCommands": commands,
    }
    return MQTTMsg(topic, payload)


def build_spyder_move_command(
        robot_label: str,
        set_id: str,
        command_id: str | int,
        init_position: int,
        target_position: int,
        vel: int,
        acc: int,
        load_sensor_front: bool = False,
        load_sensor_rear: bool = False
):
    return {
        "robotCommandLabel": f"{robot_label}-{set_id}-{command_id}",
        "previousCommandLabel": f"",
        "commandContent": {
            "robotCommandType": "MOVE",
            "coordZ": target_position,
            "maxVelocity": vel,
            "maxAcceleration": acc,
        },
        "expectedState": {
            "coordZ": init_position,
            "zTolerance": 10,
            "velocity": 0,
            "velocityTolerance": 50,
            "acceleration": 0,
            "accelerationTolerance": 50,
            "loadSensorFront": load_sensor_front,
            "loadSensorRear": load_sensor_rear,
            "antipinchSensorFront": False,
            "antipinchSensorRear": False,
            "loadSensors": {
                "front": load_sensor_front,
                "rear": load_sensor_rear,
            },
            "antiPinchSensors": {
                "d": False,
                "e": False,
            }
        },
        "futureState": {
            "coordZ": target_position,
            "zTolerance": 10,
            "velocity": 0,
            "velocityTolerance": 50,
            "acceleration": 0,
            "accelerationTolerance": 50,
            "loadSensorFront": load_sensor_front,
            "loadSensorRear": load_sensor_rear,
            "antipinchSensorFront": False,
            "antipinchSensorRear": False,
            "loadSensors": {
                "front": load_sensor_front,
                "rear": load_sensor_rear,
            },
            "antiPinchSensors": {
                "d": False,
                "e": False,
            }
        }
    }


def build_spyder_move_command_set(robot_label: str, init_pos: int, command_param: list, load_sensor_front: bool = False, load_sensor_rear: bool = False):
    topic = f"robot/commandSet/create/{robot_label}"
    set_id = f"SET-{datetime.now().isoformat()}"

    commands = []
    for command_id, (target_pos, vel, acc) in enumerate(command_param):
        commands.append(build_spyder_move_command(
            robot_label, set_id, str(command_id + 1), init_pos, target_pos, vel, acc, load_sensor_front, load_sensor_rear))
        init_pos = target_pos

    payload = {
        "robotCommandSetLabel": f"{robot_label}-{set_id}",
        "timestamp": datetime.now().isoformat(),
        "robotCommands": commands,
    }
    return MQTTMsg(topic, payload)


def build_spyder_action_command_set(robot_label: str, init_pos: int, load: bool, forward: bool, distance: int):
    topic = f"robot/commandSet/create/{robot_label}"
    set_id = f"SET-{datetime.now().isoformat()}"

    commands = [{
        "robotCommandLabel": f"{robot_label}-{set_id}-0",
        "previousCommandLabel": f"",
        "commandContent": {
            "robotCommandType": "LOAD" if load else "UNLOAD",
            "side": "FORWARD" if forward else "BACKWARD",
            "distance": distance,
        },
        "expectedState": {
            "coordZ": init_pos,
            "zTolerance": 10,
            "velocity": 0,
            "velocityTolerance": 50,
            "acceleration": 0,
            "accelerationTolerance": 50,
            "loadSensorFront": True if not load and forward else False,
            "loadSensorRear": True if not load and not forward else False,
            "antipinchSensorFront": False,
            "antipinchSensorRear": False,
            "loadSensors": {
                "front": True if not load and forward else False,
                "rear": True if not load and not forward else False,
            },
            "antiPinchSensors": {
                "d": False,
                "e": False,
            }
        },
        "futureState": {
            "coordZ": init_pos,
            "zTolerance": 10,
            "velocity": 0,
            "velocityTolerance": 50,
            "acceleration": 0,
            "accelerationTolerance": 50,
            "loadSensorFront": True if load and forward else False,
            "loadSensorRear": True if load and not forward else False,
            "antipinchSensorFront": False,
            "antipinchSensorRear": False,
            "loadSensors": {
                "front": True if load and forward else False,
                "rear": True if load and not forward else False,
            },
            "antiPinchSensors": {
                "d": False,
                "e": False,
            }
        }
    }]

    payload = {
        "robotCommandSetLabel": f"{robot_label}-{set_id}",
        "timestamp": datetime.now().isoformat(),
        "robotCommands": commands,
    }
    return MQTTMsg(topic, payload)


def build_spyder_home_command_set(
        robot_label: str,
        command_type: str,
        distance_to_dm_codes: int = 200,
        origin_offset: int = 200
):
    topic = f"robot/commandSet/create/{robot_label}"
    set_id = f"SET-{datetime.now().isoformat()}"

    commands = [
        {
            "robotCommandLabel": f"{robot_label}-{set_id}-0",
            "previousCommandLabel": f"",
            "commandContent": {
                "robotCommandType": command_type,
                "distanceToDmCodes": distance_to_dm_codes,
                "originOffset": origin_offset
            },
            "expectedState": {
                "coordZ": 0,
                "zTolerance": 10,
                "velocity": 0,
                "velocityTolerance": 50,
                "acceleration": 0,
                "accelerationTolerance": 50,
                "loadSensorFront": False,
                "loadSensorRear": False,
                "antipinchSensorFront": False,
                "antipinchSensorRear": False,
            },
            "futureState": {
                "coordZ": 0,
                "zTolerance": 10,
                "velocity": 0,
                "velocityTolerance": 50,
                "acceleration": 0,
                "accelerationTolerance": 50,
                "loadSensorFront": False,
                "loadSensorRear": False,
                "antipinchSensorFront": False,
                "antipinchSensorRear": False,
            }
        }
    ]

    payload = {
        "robotCommandSetLabel": f"{robot_label}-{set_id}",
        "timestamp": datetime.now().isoformat(),
        "robotCommands": commands,
    }
    return MQTTMsg(topic, payload)


def build_ant_action_command(
        robot_label: str,
        set_id: str,
        command_id: str | int,
        command_type: str,
        init_x: int,
        init_y: int,
        init_ori: int,
        init_lift: int,
        target_x: int,
        target_y: int,
        target_ori: int,
        target_lift: int,
        vel: int,
        acc: int
):
    return {
        "robotCommandLabel": f"{robot_label}-{set_id}-{command_id}",
        "previousCommandLabel": f"",
        "commandContent": {
            "robotCommandType": command_type,
            "coordX": target_x,
            "coordY": target_y,
            "coordZ": 0,
            "finalTargetX": target_x,
            "finalTargetY": target_y,
            "finalTargetZ": 0,
            "maxVelocity": vel,
            "maxAcceleration": acc,
            "orientation": int(target_ori * 100),
            "liftHeight": target_lift,
            "obstacleAvoidance": False
        },
        "expectedState": {
            "coordX": init_x,
            "coordY": init_y,
            "coordZ": 0,
            "xTolerance": 50,
            "yTolerance": 50,
            "zTolerance": 50,
            "orientation": int(init_ori * 100),
            "orientationTolerance": 1000,
            "velocity": 0,
            "velocityTolerance": 50,
            "acceleration": 0,
            "accelerationTolerance": 100,
            "angularVelocity": 0,
            "angularVelocityTolerance": 100,
            "angularAcceleration": 0,
            "angularAccelerationTolerance": 100,
            "liftHeight": init_lift,
            "liftHeightTolerance": 100,
            "loadSensor": False
        },
        "futureState": {
            "coordX": target_x,
            "coordY": target_y,
            "coordZ": 0,
            "xTolerance": 50,
            "yTolerance": 50,
            "zTolerance": 50,
            "orientation": int(target_ori * 100),
            "orientationTolerance": 1000,
            "velocity": 0,
            "velocityTolerance": 50,
            "acceleration": 0,
            "accelerationTolerance": 100,
            "angularVelocity": 0,
            "angularVelocityTolerance": 100,
            "angularAcceleration": 0,
            "angularAccelerationTolerance": 100,
            "liftHeight": target_lift,
            "liftHeightTolerance": 100,
            "loadSensor": False
        }
    }


def build_ant_action_command_set(robot_label: str, init_pos: tuple, command_param: list):
    topic = f"robot/commandSet/create/{robot_label}"
    set_id = f"SET-{datetime.now().isoformat()}"

    curr_state = {
        'x': init_pos[0],
        'y': init_pos[1],
        'ori': init_pos[2],
        'lift': init_pos[3]
    }

    commands = []
    for command_id, params in enumerate(command_param):
        target_state = curr_state.copy()
        vel = acc = 0
        command_type = params[0]
        if command_type == 'MOVE':
            target_state['x'] = params[1]
            target_state['y'] = params[2]
            vel = params[3]
            acc = params[4]
        elif command_type == 'SPIN':
            target_state['ori'] = params[1]
        elif command_type == 'LIFT':
            target_state['lift'] = params[1]
        command = build_ant_action_command(
            robot_label,
            set_id,
            command_id,
            command_type,
            curr_state['x'],
            curr_state['y'],
            curr_state["ori"],
            curr_state['lift'],
            target_state["x"],
            target_state["y"],
            target_state['ori'],
            target_state["lift"],
            vel,
            acc)
        commands.append(command)
        curr_state = target_state

    payload = {
        "robotCommandSetLabel": f"{robot_label}-{set_id}",
        "timestamp": datetime.now().isoformat(),
        "robotCommands": commands,
    }
    return MQTTMsg(topic, payload)


def build_robot_command(robot_label: str, set_id: str, command_type: str, command_id: str | int = 0):
    return {
        "robotCommandLabel": f"{robot_label}-{set_id}-{command_id}",
        "previousCommandLabel": f"",
        "commandContent": {
            "robotCommandType": command_type
        },
        "expectedState": {
            "coordX": 0,
            "coordY": 0,
            "coordZ": 0,
            "xTolerance": 10,
            "yTolerance": 10,
            "zTolerance": 10,
            "orientation": 0,
            "orientationTolerance": 200,
            "velocity": 0,
            "velocityTolerance": 50,
            "acceleration": 0,
            "accelerationTolerance": 100,
            "angularVelocity": 0,
            "angularVelocityTolerance": 100,
            "angularAcceleration": 0,
            "angularAccelerationTolerance": 100,
            "liftHeight": 0,
            "liftHeightTolerance": 100,
            "loadSensor": False,
            "loadSensorFront": False,
            "loadSensorRear": False,
            "antipinchSensorFront": False,
            "antipinchSensorRear": False,
        },
        "futureState": {
            "coordX": 0,
            "coordY": 0,
            "coordZ": 0,
            "xTolerance": 10,
            "yTolerance": 10,
            "zTolerance": 10,
            "orientation": 0,
            "orientationTolerance": 200,
            "velocity": 0,
            "velocityTolerance": 50,
            "acceleration": 0,
            "accelerationTolerance": 100,
            "angularVelocity": 0,
            "angularVelocityTolerance": 100,
            "angularAcceleration": 0,
            "angularAccelerationTolerance": 100,
            "liftHeight": 0,
            "liftHeightTolerance": 100,
            "loadSensor": False,
            "loadSensorFront": False,
            "loadSensorRear": False,
            "antipinchSensorFront": False,
            "antipinchSensorRear": False,
        }
    }


def build_robot_command_set(robot_label: str, command_type: str):
    topic = f"robot/commandSet/create/{robot_label}"
    set_id = f"SET-{datetime.now().isoformat()}"

    commands = [build_robot_command(robot_label, set_id, command_type)]
    payload = {
        "robotCommandSetLabel": f"{robot_label}-{set_id}",
        "timestamp": datetime.now().isoformat(),
        "robotCommands": commands,
    }
    return MQTTMsg(topic, payload)
