import json
import time


from helper import *


def main(args):
    print(args)

    ant = Ant(args.ant)
    helper = Helper(robot_list=[ant])
    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(host=args.server_ip, port=args.server_port,
                      username=args.username, password=args.password)
    mqtt_client.add_robot(ant.robot_label)

    payload = {
        "robotCommandSetLabel": "TEST-HALT",
        "timestamp": "2024-07-31T16:44:49.988994560Z",
        "robotCommands": [
            {
                "robotCommandLabel": "TEST-HALT-1",
                "previousCommandLabel": f"",
                "commandContent": {
                    "robotCommandType": "MOVE",
                    "coordX": 104000,
                    "coordY": 105000,
                    "coordZ": 0,
                    "maxVelocity": 2000,
                    "maxAcceleration": 500,
                    "finalTargetX": 107000,
                    "finalTargetY": 105000,
                    "finalTargetZ": 0,
                    "obstacleAvoidance": False
                },
                "expectedState": {
                    "coordX": 100000,
                    "coordY": 105000,
                    "coordZ": 0,
                    "xTolerance": 15,
                    "yTolerance": 15,
                    "zTolerance": 15,
                    "orientation": 0,
                    "orientationTolerance": 200,
                    "velocity": 0,
                    "velocityTolerance": 50,
                    "acceleration": 0,
                    "accelerationTolerance": 0,
                    "angularVelocity": 0,
                    "angularVelocityTolerance": 0,
                    "angularAcceleration": 0,
                    "angularAccelerationTolerance": 0,
                    "liftHeight": 0,
                    "liftHeightTolerance": 20,
                    "loadSensor": False
                },
                "futureState": {
                    "coordX": 104000,
                    "coordY": 105000,
                    "coordZ": 0,
                    "xTolerance": 5,
                    "yTolerance": 5,
                    "zTolerance": 5,
                    "orientation": 0,
                    "orientationTolerance": 1000,
                    "velocity": 2000,
                    "velocityTolerance": 1,
                    "acceleration": 0,
                    "accelerationTolerance": 0,
                    "angularVelocity": 0,
                    "angularVelocityTolerance": 0,
                    "angularAcceleration": 0,
                    "angularAccelerationTolerance": 0,
                    "liftHeight": 0,
                    "liftHeightTolerance": 20,
                    "loadSensor": False
                }
            }
        ]
    }

    recover_payload = {
        "robotCommandSetLabel": "RECOVER-HALT",
        "timestamp": "2024-07-31T16:44:49.988994560Z",
        "robotCommands": [
            {
                "robotCommandLabel": "RECOVER-HALT-1",
                "previousCommandLabel": f"",
                "commandContent": {
                    "robotCommandType": "MOVE",
                    "coordX": 108000,
                    "coordY": 105000,
                    "coordZ": 0,
                    "maxVelocity": 2000,
                    "maxAcceleration": 500,
                    "finalTargetX": 107000,
                    "finalTargetY": 105000,
                    "finalTargetZ": 0,
                    "obstacleAvoidance": False
                },
                "expectedState": {
                    "coordX": 106200,
                    "coordY": 105000,
                    "coordZ": 0,
                    "xTolerance": 250,
                    "yTolerance": 250,
                    "zTolerance": 100,
                    "orientation": 0,
                    "orientationTolerance": 1000,
                    "velocity": 0,
                    "velocityTolerance": 50,
                    "acceleration": 0,
                    "accelerationTolerance": 0,
                    "angularVelocity": 0,
                    "angularVelocityTolerance": 0,
                    "angularAcceleration": 0,
                    "angularAccelerationTolerance": 0,
                    "liftHeight": 0,
                    "liftHeightTolerance": 20,
                    "loadSensor": False
                },
                "futureState": {
                    "coordX": 108000,
                    "coordY": 105000,
                    "coordZ": 0,
                    "xTolerance": 100,
                    "yTolerance": 100,
                    "zTolerance": 100,
                    "orientation": 0,
                    "orientationTolerance": 1000,
                    "velocity": 0,
                    "velocityTolerance": 500,
                    "acceleration": 0,
                    "accelerationTolerance": 0,
                    "angularVelocity": 0,
                    "angularVelocityTolerance": 0,
                    "angularAcceleration": 0,
                    "angularAccelerationTolerance": 0,
                    "liftHeight": 0,
                    "liftHeightTolerance": 20,
                    "loadSensor": False
                }
            },
            {
                "robotCommandLabel": "RECOVER-HALT-2",
                "previousCommandLabel": f"",
                "commandContent": {
                    "robotCommandType": "MOVE",
                    "coordX": 100000,
                    "coordY": 105000,
                    "coordZ": 0,
                    "maxVelocity": 2000,
                    "maxAcceleration": 500,
                    "finalTargetX": 100000,
                    "finalTargetY": 105000,
                    "finalTargetZ": 0,
                    "obstacleAvoidance": False
                },
                "expectedState": {
                    "coordX": 108000,
                    "coordY": 105000,
                    "coordZ": 0,
                    "xTolerance": 100,
                    "yTolerance": 100,
                    "zTolerance": 100,
                    "orientation": 0,
                    "orientationTolerance": 1000,
                    "velocity": 0,
                    "velocityTolerance": 50,
                    "acceleration": 0,
                    "accelerationTolerance": 0,
                    "angularVelocity": 0,
                    "angularVelocityTolerance": 0,
                    "angularAcceleration": 0,
                    "angularAccelerationTolerance": 0,
                    "liftHeight": 0,
                    "liftHeightTolerance": 20,
                    "loadSensor": False
                },
                "futureState": {
                    "coordX": 100000,
                    "coordY": 105000,
                    "coordZ": 0,
                    "xTolerance": 100,
                    "yTolerance": 100,
                    "zTolerance": 100,
                    "orientation": 0,
                    "orientationTolerance": 1000,
                    "velocity": 0,
                    "velocityTolerance": 500,
                    "acceleration": 0,
                    "accelerationTolerance": 0,
                    "angularVelocity": 0,
                    "angularVelocityTolerance": 0,
                    "angularAcceleration": 0,
                    "angularAccelerationTolerance": 0,
                    "liftHeight": 0,
                    "liftHeightTolerance": 20,
                    "loadSensor": False
                }
            }
        ]
    }

    # 将 payload 转换为 JSON 字符串
    payload_json = json.dumps(payload)

    try:
        # wait for robot online and report its state
        while ant.state_update_flag is False:
            time.sleep(1)

        # init ant
        while ant.state == "UNKNOWN":
            msg = build_robot_command_set(ant.robot_label, "INIT")

            mqtt_client.publish(
                robot_label=ant.robot_label, topic=msg.topic, payload=msg.payload)

            time.sleep(2)

        # check robot init state
        while ant.state != "IDLE":
            time.sleep(1)

        mqtt_client.publish(
            robot_label=ant.robot_label, payload=payload)

        time.sleep(8)

        mqtt_client.publish(
            robot_label=ant.robot_label, payload=recover_payload)

    except KeyboardInterrupt:
        pass
    finally:
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
