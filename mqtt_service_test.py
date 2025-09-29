import json
import subprocess
import sys
import time
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
        self.topic = topic
        if isinstance(payload, str):
            payload = json.dumps(json.loads(payload), indent=4)
        self.payload = payload

    def __str__(self):
        return f"MQTTMessage(topic={self.topic}, payload={self.payload})"


class MQTTClient:
    __on_receive_callback = None

    def __init__(self, client_id="paho-mqtt", callback=None):
        self.client_id = client_id + "-" + str(datetime.now().isoformat())
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id,
        )
        self.__on_receive_callback = callback
        self.log = LogTool("mqtt", "mqtt.log").get_logger()

        self.connected = False
        self.stop_flag = False
        self.subscriptions = []  # 保存订阅记录，断线重连后恢复

    def __on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            self.log.info(f"MQTT客户端 {self.client_id} 已连接")
            # 断线重连后恢复订阅
            for topic, qos in self.subscriptions:
                client.subscribe(topic, qos)
                self.log.info(f"已恢复订阅: {topic}")
        else:
            self.connected = False
            self.log.error(f"MQTT连接失败，返回码: {rc}")

    def __on_disconnect(self, client, userdata, rc, properties=None):
        self.connected = False
        if self.stop_flag:
            return
        self.log.warning(f"MQTT客户端 {self.client_id} 断开连接，返回码: {rc}，尝试重连...")
        while not self.connected and not self.stop_flag:
            try:
                client.reconnect()
                self.connected = True
                self.log.info("MQTT重连成功")
            except Exception as e:
                self.log.error(f"MQTT重连失败: {e}")
                time.sleep(3)

    def __on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode("utf-8")
            message = MQTTMsg(topic=msg.topic, payload=payload_str)
            self.log.info(f"接收 <- {message}")
            if self.__on_receive_callback:
                self.__on_receive_callback(message)
        except Exception as e:
            self.log.error(f"MQTT消息解析失败: {e}")

    def start(self, host="localhost", port=1883, username='', password=''):
        self.client.on_connect = self.__on_connect
        self.client.on_message = self.__on_message
        self.client.on_disconnect = self.__on_disconnect
        self.client.username_pw_set(username, password)
        self.client.connect(host, port, keepalive=30)
        self.client.loop_start()
        self.log.info(f"MQTT客户端: {self.client_id} 已启动")

    def stop(self):
        self.stop_flag = True
        self.client.disconnect()
        self.client.loop_stop()
        self.log.info(f"MQTT客户端: {self.client_id} 已关闭")

    def subscribe(self, topic, qos=2):
        self.subscriptions.append((topic, qos))
        self.client.subscribe(topic, qos)

    def publish(self, robot_label="", topic="", payload=None, qos=2, retain=False):
        if payload is None:
            payload = {}
        if not topic:
            topic = f"robot/commandSet/create/{robot_label}"
        if isinstance(payload, dict):
            payload = json.dumps(payload, indent=2)
        self.client.publish(topic, str(payload), qos, retain)
        self.log.info(f"发送 -> {MQTTMsg(topic=topic, payload=payload)}")

    def add_robot(self, robot_label):
        self.subscribe(f"robot/state/{robot_label}")
        self.subscribe(f"robot/command/status/{robot_label}")
        self.subscribe(f"robot/commandSet/create/{robot_label}")

    def wait_for_state_update(self, robot, timeout=5):
        """等待机器人状态更新，带超时"""
        start_time = time.time()
        while not robot.state_update_flag:
            if not self.connected:
                self.log.warning("等待状态时MQTT已断开，等待重连...")
            if time.time() - start_time > timeout:
                self.log.warning(f"{robot.robot_label} 等待状态超时")
                return False
            time.sleep(0.05)
        return True
