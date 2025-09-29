import json
import subprocess
import sys
from datetime import datetime

from LogTool import LogTool

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("paho-mqtt not found, installing...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "paho-mqtt"])
finally:
    import paho.mqtt.client as mqtt


class MQTTMsg:
    def __init__(self, topic, payload):
        super().__init__()
        self.topic = topic
        if isinstance(payload, str):
            payload = json.dumps(json.loads(payload), indent=4)
        self.payload = payload

    def __str__(self):
        return f"MQTTMessage(topic={self.topic}, payload={self.payload})"

    def __repr__(self):
        return f"MQTTMessage(topic={self.topic}, payload={self.payload})"


class MQTTClient:
    __on_receive_callback = None

    def __init__(
            self,
            client_id="paho-mqtt",
            callback=None
    ):
        # generate a unique client ID = client_id + current time
        self.client_id = client_id + "-" + str(datetime.now().isoformat())
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=self.client_id,
        )
        self.__on_receive_callback = callback
        self.log = LogTool("mqtt", "mqtt.log").get_logger()

    def __on_connect(self, client, dummy, userdata, flags, rc):
        """
        mqttc.on_connect is an instance method.
        It implicitly passes the instance as the first argument to the method (usually known as self)
        However, the callback function is inside the class, so
            the first argument is the instance itself,
            the second argument will be the client,
            the third argument will be None.
        """
        pass

    def __on_message(self, client, userdata, msg):
        message = MQTTMsg(topic=msg.topic, payload=msg.payload.decode("utf-8"))
        self.log.info(f"接收 <- {message}")
        if self.__on_receive_callback:
            self.__on_receive_callback(message)

    def start(self, host="localhost", port=1883, username='', password=''):
        self.client.on_connect = self.__on_connect  # bind function to callback
        self.client.on_message = self.__on_message
        self.client.username_pw_set(username, password)
        self.client.connect(host, port)  # connect to broker
        self.client.loop_start()  # start loop to process received messages
        self.log.info(f"MQTT客户端: {self.client_id} 已启动")

    def stop(self):
        self.client.disconnect()
        self.client.loop_stop()
        self.log.info(f"MQTT客户端: {self.client_id} 已关闭")

    def subscribe(self, topic, qos=2):
        self.client.subscribe(topic, qos)

    def publish(self, robot_label="", topic="", payload=None, qos=2, retain=False):
        if payload is None:
            payload = {}
        if not topic:
            topic = "robot/commandSet/create/" + robot_label
        if isinstance(payload, dict):
            payload = json.dumps(payload, indent=2)
        self.client.publish(topic, str(payload), qos, retain)
        self.log.info(f"发送 -> {MQTTMsg(topic=topic, payload=payload)}")

    def add_robot(self, robot_label):
        self.subscribe(f"robot/state/{robot_label}")
        self.subscribe(f"robot/command/status/{robot_label}")
        self.subscribe(f"robot/commandSet/create/{robot_label}")
        # self.subscribe(f"robot/config/updated/+")
