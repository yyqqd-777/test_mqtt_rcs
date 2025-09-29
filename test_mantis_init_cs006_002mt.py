import time
from helper import *


def main(args):
    print(args)

    mantis = Mantis(args.mantis)
    helper = Helper(robot_list=[mantis])
    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(host=args.server_ip, port=args.server_port,
                      username=args.username, password=args.password)
    mqtt_client.add_robot(mantis.robot_label)

    try:
        # 机器人初始化
        while mantis.state != "UNKNOWN":
            time.sleep(1)

        # INIT
        print("INIT")
        msg = build_robot_command_set(mantis.robot_label, "INIT")

        mqtt_client.publish(
            robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload)

        while mantis.state != "LOCATION_UNKNOWN":
            time.sleep(1)
        # return
        # HOME_MANTIS_FIRST_CODE
        print("HOME_MANTIS_FIRST_CODE")
        msg = build_mantis_home_command_set(
            mantis.robot_label, command_type="HOME_MANTIS_FIRST_CODE", distance_to_dm_codes=990, distance_between_dm_codes=1)
            # mantis.robot_label, command_type="HOME_MANTIS_FIRST_CODE", distance_to_dm_codes=1010, distance_between_dm_codes=5)

        mqtt_client.publish(
            robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload
        )
        command_result = msg.payload["robotCommands"][-1]["robotCommandLabel"]
        while helper.complete_command[mantis.robot_label] != command_result:
            time.sleep(0.05)

        while mantis.state != "LOCATION_UNKNOWN":
            time.sleep(1)

        # HOME_SET_ORIGIN
        print("INIHOME_SET_ORIGINT")
        msg = build_mantis_home_command_set(
            mantis.robot_label, command_type="HOME_SET_ORIGIN", origin_offset_x=0, origin_offset_z=500)

        mqtt_client.publish(
            robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload)

        while mantis.state != "LOCATION_KNOWN":
            time.sleep(1)

        # return
        # HOME_HANDLER
        print("HOME_HANDLER")
        msg = build_home_command_set_simple(
            mantis.robot_label, command_type="HOME_HANDLER")

        mqtt_client.publish(
            robot_label=mantis.robot_label, topic=msg.topic, payload=msg.payload
        )
        command_result = msg.payload["robotCommands"][-1]["robotCommandLabel"]
        while helper.complete_command[mantis.robot_label] != command_result:
            time.sleep(0.05)

        while mantis.state != "IDLE":
            time.sleep(1)

    except KeyboardInterrupt:
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
