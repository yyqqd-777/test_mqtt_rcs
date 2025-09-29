import json
import time

import paho.mqtt.client as mqtt

# 创建 MQTT 客户端实例
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="retained-configs",
)

# 连接到 MQTT 服务器
client.username_pw_set("EE17G1eA", "EE17G1eB")
client.connect("10.0.7.136", 1883, 60)  # 请将地址替换为实际 MQTT 服务器的地址


topic = "robot/commandSet/create/A266"

init_y = 106000
target_y = 106869

step = (target_y - init_y) // 3

payload = {
    "robotCommandSetLabel": "A100-S10",
    "timestamp": "2024-07-31T16:44:49.988994560Z",
    "robotCommands": [
        {
            "robotCommandLabel": "A100-S9-0",
            "commandContent": {
                "robotCommandType": "MOVE",
                "coordX": 103000,
                "coordY": init_y + step,
                "coordZ": 0,
                "maxVelocity": 500,
                "maxAcceleration": 500,
                "finalTargetX": 103000,
                "finalTargetY": init_y + step * 3,
                "finalTargetZ": 0
            },
            "expectedState": {
                "coordX": 103000,
                "coordY": init_y,
                "coordZ": 0,
                "xTolerance": 100,
                "yTolerance": 100,
                "zTolerance": 100,
                "orientation": 9000,
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
                "coordX": 103000,
                "coordY": init_y + step,
                "coordZ": 0,
                "xTolerance": 100,
                "yTolerance": 100,
                "zTolerance": 100,
                "orientation": 9000,
                "orientationTolerance": 1000,
                "velocity": 500,
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
            }
        },
        {
            "robotCommandLabel": "A100-S9-1",
            "commandContent": {
                "robotCommandType": "MOVE",
                "coordX": 103000,
                "coordY": init_y + step * 2,
                "coordZ": 0,
                "maxVelocity": 500,
                "maxAcceleration": 500,
                "finalTargetX": 103000,
                "finalTargetY": init_y + step * 3,
                "finalTargetZ": 0
            },
            "expectedState": {
                "coordX": 103000,
                "coordY": init_y + step,
                "coordZ": 0,
                "xTolerance": 100,
                "yTolerance": 100,
                "zTolerance": 100,
                "orientation": 9000,
                "orientationTolerance": 1000,
                "velocity": 500,
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
                "coordX": 103000,
                "coordY": init_y + step * 2,
                "coordZ": 0,
                "xTolerance": 100,
                "yTolerance": 100,
                "zTolerance": 100,
                "orientation": 9000,
                "orientationTolerance": 1000,
                "velocity": 500,
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
            }
        },
        {
            "robotCommandLabel": "A100-S9-2",
            "commandContent": {
                "robotCommandType": "MOVE",
                "coordX": 103000,
                "coordY": init_y + step * 3,
                "coordZ": 0,
                "maxVelocity": 500,
                "maxAcceleration": 500,
                "finalTargetX": 103000,
                "finalTargetY": init_y + step * 3,
                "finalTargetZ": 0
            },
            "expectedState": {
                "coordX": 103000,
                "coordY": init_y + step * 2,
                "coordZ": 0,
                "xTolerance": 100,
                "yTolerance": 100,
                "zTolerance": 100,
                "orientation": 9000,
                "orientationTolerance": 1000,
                "velocity": 500,
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
                "coordX": 103000,
                "coordY": init_y + step * 3,
                "coordZ": 0,
                "xTolerance": 100,
                "yTolerance": 100,
                "zTolerance": 100,
                "orientation": 9000,
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
            }
        }
    ]
}

init_y, target_y = target_y, init_y

payload_2 = {
    "robotCommandSetLabel": "A100-S10",
    "timestamp": "2024-07-31T16:44:49.988994560Z",
    "robotCommands": [
        {
            "robotCommandLabel": "A100-S9-0",
            "commandContent": {
                "robotCommandType": "MOVE",
                "coordX": 103000,
                "coordY": init_y - step,
                "coordZ": 0,
                "maxVelocity": 500,
                "maxAcceleration": 500,
                "finalTargetX": 103000,
                "finalTargetY": init_y - step * 3,
                "finalTargetZ": 0
            },
            "expectedState": {
                "coordX": 103000,
                "coordY": init_y,
                "coordZ": 0,
                "xTolerance": 100,
                "yTolerance": 100,
                "zTolerance": 100,
                "orientation": 9000,
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
                "coordX": 103000,
                "coordY": init_y - step,
                "coordZ": 0,
                "xTolerance": 100,
                "yTolerance": 100,
                "zTolerance": 100,
                "orientation": 9000,
                "orientationTolerance": 1000,
                "velocity": 500,
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
            }
        },
        {
            "robotCommandLabel": "A100-S9-1",
            "commandContent": {
                "robotCommandType": "MOVE",
                "coordX": 103000,
                "coordY": init_y - step * 2,
                "coordZ": 0,
                "maxVelocity": 500,
                "maxAcceleration": 500,
                "finalTargetX": 103000,
                "finalTargetY": init_y - step * 3,
                "finalTargetZ": 0
            },
            "expectedState": {
                "coordX": 103000,
                "coordY": init_y - step,
                "coordZ": 0,
                "xTolerance": 100,
                "yTolerance": 100,
                "zTolerance": 100,
                "orientation": 9000,
                "orientationTolerance": 1000,
                "velocity": 500,
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
                "coordX": 103000,
                "coordY": init_y - step * 2,
                "coordZ": 0,
                "xTolerance": 100,
                "yTolerance": 100,
                "zTolerance": 100,
                "orientation": 9000,
                "orientationTolerance": 1000,
                "velocity": 500,
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
            }
        },
        {
            "robotCommandLabel": "A100-S9-2",
            "commandContent": {
                "robotCommandType": "MOVE",
                "coordX": 103000,
                "coordY": init_y - step * 3,
                "coordZ": 0,
                "maxVelocity": 500,
                "maxAcceleration": 500,
                "finalTargetX": 103000,
                "finalTargetY": init_y - step * 3,
                "finalTargetZ": 0
            },
            "expectedState": {
                "coordX": 103000,
                "coordY": init_y - step * 2,
                "coordZ": 0,
                "xTolerance": 100,
                "yTolerance": 100,
                "zTolerance": 100,
                "orientation": 9000,
                "orientationTolerance": 1000,
                "velocity": 500,
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
                "coordX": 103000,
                "coordY": init_y - step * 3,
                "coordZ": 0,
                "xTolerance": 100,
                "yTolerance": 100,
                "zTolerance": 100,
                "orientation": 9000,
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
            }
        }
    ]
}

# 将 payload 转换为 JSON 字符串
payload_json = json.dumps(payload)
payload_json_2 = json.dumps(payload_2)

for _ in range(10):
    # 发布消息
    client.publish(
        topic=topic, payload=payload_json, qos=2, retain=False)

    time.sleep(5)

    client.publish(
        topic=topic, payload=payload_json_2, qos=2, retain=False)

    time.sleep(5)


# 断开连接
client.disconnect()
