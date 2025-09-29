import json
import signal
import sys
import paho.mqtt.client as mqtt


# ---------- 回调函数 ----------
def on_connect(client, userdata, flags, reason_code, properties=None):
    print("🔌 [on_connect] reason_code =", reason_code)
    if reason_code == 0:
        print("✅ 已成功连接到 MQTT Broker")
    else:
        print(f"❌ 连接失败，返回码: {reason_code}")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties=None):
    print("🔌 [on_disconnect] disconnect_flags =", disconnect_flags)
    print("🔌 [on_disconnect] reason_code =", reason_code)
    if properties:
        print("🔌 [on_disconnect] properties =", properties)


def on_publish(client, userdata, mid, reason_code=None, properties=None):
    print(f"📤 [on_publish] 消息发布完成 (mid={mid}, reason_code={reason_code})")


def on_log(client, userdata, level, buf):
    print(f"🪵 [on_log] level={level}, msg={buf}")


# ---------- 优雅退出 ----------
def handle_exit(signum, frame):
    print("\n🛑 捕获到退出信号 (Ctrl+C / kill)，正在断开 MQTT 连接 ...")
    try:
        client.disconnect()
    except Exception as e:
        print("⚠️ 断开时异常:", e)
    sys.exit(0)


# 捕获 Ctrl+C / kill
signal.signal(signal.SIGINT, handle_exit)   # Ctrl+C
signal.signal(signal.SIGTERM, handle_exit)  # kill


# ---------- 创建 MQTT 客户端 ----------
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="retained-configs",
)
client.username_pw_set("EE17G1eA", "EE17G1eB")

# 绑定调试回调
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.on_log = on_log   # 🔧 开启日志回调

# 连接到 MQTT 服务器
print("🚀 尝试连接 MQTT Broker ...")
client.connect("10.0.7.136", 1883)


# ---------- 发布配置 ----------
config = {
    "02049FC910D1": {
        "robotLabel": "M502",
        "footOriginOffset": 70,
        "maximumTargetX": 10000,
        "minimumTargetX": -500,
        "maximumTargetZ": 7000,
        "minimumTargetZ": -500,
        "libraryReverseX": False,
    }
}

for robot_id, payload in config.items():
    payload_json = json.dumps(payload)
    topic = f"robot/config/updated/{robot_id}"

    print(f"\n📌 准备发布: topic={topic}, payload={payload_json}")

    info = client.publish(
        topic,
        payload=payload_json,
        qos=2,
        retain=True,
    )

    print(f"⏳ [等待中] mid={info.mid} 发布确认中 ...")
    info.wait_for_publish()

    if info.is_published():
        print(f"✅ 配置已发布成功: {robot_id}")
    else:
        print(f"❌ 配置发布失败: {robot_id}")


# ---------- 主循环，等待退出 ----------
print("⌛ 发布完成，进入等待状态 (按 Ctrl+C 可退出)...")
client.loop_forever()
