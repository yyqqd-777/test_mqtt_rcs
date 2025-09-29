from datetime import datetime
from mqtt_service import MQTTMsg


def build_general_command_set_simple(
    robot_label: str,
    command_content: dict,
    expect: dict = None,
    future: dict = None
):
    topic = f"robot/commandSet/create/{robot_label}"
    set_id = f"SET-{datetime.now().isoformat()}"

    command = {
        "robotCommandLabel": f"{robot_label}-{set_id}-0",
        "previousCommandLabel": "",
        "commandContent": command_content,
    }
    if expect:
        command["expectedState"] = expect
    if future:
        command["futureState"] = future

    payload = {
        "robotCommandSetLabel": f"{robot_label}-{set_id}",
        "timestamp": datetime.now().isoformat(),
        "robotCommands": [command],
    }
    return MQTTMsg(topic, payload)


def build_general_command_set_multiple(
    robot_label: str,
    commands: list,
):
    topic = f"robot/commandSet/create/{robot_label}"
    set_id = f"SET-{datetime.now().isoformat()}"

    payload = {
        "robotCommandSetLabel": f"{robot_label}-{set_id}",
        "timestamp": datetime.now().isoformat(),
        "robotCommands": commands,
    }

    return MQTTMsg(topic, payload)


def build_articulate_fingers_command_set_simple(
    robot_label: str,
    pos: list = [],
    expect: dict() = None,
    future: dict() = None
):
    command_content = {
        "robotCommandType": "ARTICULATE_FINGERS",
        "fingerPosition": {
            "left1": pos[0],
            "left2": pos[1],
            "left3": pos[2],
            "left4": pos[3],
            "right1": pos[4],
            "right2": pos[5],
            "right3": pos[6],
            "right4": pos[7],
        }
    }
    return build_general_command_set_simple(robot_label, command_content, expect, future)


def build_move_arms_command_set_simple(
    robot_label: str,
    arm_position: int = 0,
    max_velocity: int = 500,
    max_acceleration: int = 500,
    expect: dict() = None,
    future: dict() = None
):
    command_content = {
        "robotCommandType": "MOVE_ARMS",
        "armPosition": arm_position,
        "maxVelocity": max_velocity,
        "maxAcceleration": max_acceleration
    }
    return build_general_command_set_simple(robot_label, command_content, expect, future)


def build_load_command_set_simple(
    robot_label: str,
    load: bool,
    forward: bool,
    distance: int,
    expect: dict() = None,
    future: dict() = None
):
    command_content = {
        "robotCommandType": "LOAD" if load else "UNLOAD",
        "side": "FORWARD" if forward else "BACKWARD",
        "distance": distance,
    }
    return build_general_command_set_simple(robot_label, command_content, expect, future)


def build_home_command_set_simple(
    robot_label: str,
    command_type: str,
    distance_to_dm_codes: int = 200,
    origin_offset: int = 200,
    expect: dict() = None,
    future: dict() = None
):
    command_content = {
        "robotCommandType": command_type,
        "distanceToDmCodes": distance_to_dm_codes,
        "originOffset": origin_offset
    }
    return build_general_command_set_simple(robot_label, command_content, expect, future)


# 可以根据实际需要传入expectedState和futureState
def build_robot_command_set_simple(
    robot_label: str,
    command_type: str,
    expect: dict() = None,
    future: dict() = None
):
    command_content = {
        "robotCommandType": command_type
    }
    return build_general_command_set_simple(robot_label, command_content, expect, future)
