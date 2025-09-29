import time

from helper import *


def main(args):
    print(args)

    robot = Robot("Mantis", args.mantis)
    helper = Helper(robot_list=[robot])
    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(host=args.server_ip, port=args.server_port,
                      username=args.username, password=args.password)
    mqtt_client.add_robot(robot.robot_label)

    try:
        while not robot.state_update_flag:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
