import json

import paho.mqtt.client as mqtt

# 创建 MQTT 客户端实例
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="retained-configs",
)

# 连接到 MQTT 服务器
client.username_pw_set("EE17G1eA", "EE17G1eB")
client.connect("10.0.7.136", 1883)
# client.connect("192.168.2.220", 1883)

# 要发送的字典类型的 payload
config = dict()
# config["02049FC91892"] = {
#     "robotLabel": "M13221",
#     "footOriginOffset": 30,
#     "maximumTargetX": 15000,
#     "minimumTargetX": -10,
#     "maximumTargetZ": 7000,
#     "minimumTargetZ": -10,
#     "libraryReverseX": False
# }

# config["02049FC138DE"] = {
#     "robotLabel": "M503",
#     "footOriginOffset": 70,
#     "maximumTargetX": 10000,
#     "minimumTargetX": -500,
#     "maximumTargetZ": 7000,
#     "minimumTargetZ": -500,
#     "libraryReverseX": False
# }

# config["02049FB92392"] = {
#     "robotLabel": "M01",
#     "footOriginOffset": 103,
#     "maximumTargetX": 10000,
#     "minimumTargetX": -500,
#     "maximumTargetZ": 7000,
#     "minimumTargetZ": -500,
#     "libraryReverseX": False
# }

# config["02049FC13822"] = {
#     "robotLabel": "M02",
#     "footOriginOffset": 70,
#     "maximumTargetX": 10000,
#     "minimumTargetX": -500,
#     "maximumTargetZ": 7000,
#     "minimumTargetZ": -500,
#     "libraryReverseX": False
# }

# config["02049FC910D1"] = {
#     "robotLabel": "M502",
#     "footOriginOffset": 70,
#     "maximumTargetX": 10000,
#     "minimumTargetX": -500,
#     "maximumTargetZ": 7000,
#     "minimumTargetZ": -500,
#     "libraryReverseX": False,
#     "dmCodeSize": 225
# }

# config["02049F79086D"] = {
#     "robotLabel": "M13601",
#     "footOriginOffset": 30,
#     "maximumTargetX": 3500,
#     "minimumTargetX": -500,
#     "maximumTargetZ": 2010,
#     "minimumTargetZ": -10,
#     "libraryReverseX": False
# }

config["02049FC90BBC"] = {
    "robotLabel": "M603",
    "footOriginOffset": 30,
    "maximumTargetX": 15000,
    "minimumTargetX": -10,
    "maximumTargetZ": 7000,
    "minimumTargetZ": -10,
    "libraryReverseX": False,
    "dmCodeSize": 225
}

# config["02049FC92C88"] = {
#     "robotLabel": "M-A1-S1-1",
#     "footOriginOffset": 103,
#     "maximumTargetX": 15000,
#     "minimumTargetX": -10,
#     "maximumTargetZ": 7000,
#     "minimumTargetZ": -10,
#     "libraryReverseX": False,
#     "dmCodeSize": 225
# }

# config["C82E18C82B2C"] = {
#     "robotLabel": "M13216",
#     "footOriginOffset": 30,
#     "maximumTargetX": 15000,
#     "minimumTargetX": -10,
#     "maximumTargetZ": 7000,
#     "minimumTargetZ": -10,
#     "libraryReverseX": False
# }
# config["02049FC91892"] = {
#     "robotLabel": "M13216",
#     "dmSeparator": "HC",
#     "footFactor": 320.00,
#     "footOriginOffset": 30,
#     "footVelocity": 600,
#     "footAcceleration": 300,
#     "footDeceleration": 300,
#     "libraryReverseX": False
# }
# config["861740060035507"] = {
#     "robotLabel": "A103",
#     "dmSeparator": "AA",
#     "tofEnable": True,
#     "tofSafeDistance": 20,
#     "cameraOffsetTheta": 0.17,
#     "cruisingVelocity": 2000,
#     "acceleration": 500,
#     "deceleration": 500,
#     "rotateCruisingVelocity": 18000,
#     "rotateAcceleration": 15000,
#     "rotateDeceleration": 15000,
#     "wheelDiameter": 14980,
#     "wheelInterval": 44000,
#     "resolution": 10000,
#     "reductionRatio": 0.111111,
#     "feedForward": 500,
#     "linearKp": 260,
#     "linearKi": 2,
#     "linearKd": 125,
#     "scissorArm": 130,
#     "scissorBase": 250,
#     "scissorPitch": 4,
#     "scissorNumber": 1
# }

# config["861740060036398"] = {
#     "robotLabel": "L100",
#     "footFactor": 320.0,
#     "footVelocity": 500,
#     "footAcceleration": 300,
#     "footDeceleration": 300,
#     "libraryReverseX": False
# }

# config["861740060036661"] = {
#     "robotLabel": "S100",
#     "dmSeparator": "HC",
#     "footFactor": 320.00,
#     "footOriginOffset": 0,
#     "footVelocity": 600,
#     "footAcceleration": 300,
#     "footDeceleration": 300,
#     "libraryReverseX": False
# }

# config["861740060035382"] = {
#     "robotLabel": "S101",
#     "dmSeparator": "HC",
#     "footFactor": 320.00,
#     "footOriginOffset": 0,
#     "footVelocity": 600,
#     "footAcceleration": 300,
#     "footDeceleration": 300,
#     "libraryReverseX": False
# }

# config = dict()
# config["083A8D8B8A8C"] = {
#     "robotLabel": "KING-CRAB",
#     "footFactor": 320.00,
#     "footOriginOffset": 0,
#     "libraryReverseX": False,
#     "minimumTarget": -1000,
#     "maximumTarget": 5000
# }

# config["1C6920CAF1CC"] = {
#     "robotLabel": "CROCODILE",
#     "dmSeparator": "GG",
#     "tofEnable": True,
#     "tofSafeDistance": 20,
#     "cameraOffsetTheta": 0,
#     "cruisingVelocity": 1000,
#     "acceleration": 500,
#     "deceleration": 500,
#     "rotateCruisingVelocity": 18000,
#     "rotateAcceleration": 15000,
#     "rotateDeceleration": 15000,
#     "wheelDiameter": 15000,
#     "wheelInterval": 48000,
#     "resolution": 10000,
#     "reductionRatio": 0.111111,
#     "feedForward": 500,
#     "linearKp": 300,
#     "linearKi": 2,
#     "linearKd": 125,
#     "scissorArm": 150,
#     "scissorBase": 296,
#     "scissorPitch": 2,
#     "scissorNumber": 2
# }

for id, payload in config.items():
    # 将 payload 转换为 JSON 字符串
    payload_json = json.dumps(payload)

    # 发布消息
    client.publish(
        f"robot/config/updated/{id}", payload=payload_json, qos=2, retain=True)
    print(f"published {id}")

# 断开连接
client.disconnect()
