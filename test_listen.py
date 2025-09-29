import time

from helper import *


def main(args):
    print(args)

    spyder_labels = ['S' + str(i) for i in range(300, 350)]
    ladder_labels = ['L' + str(i) for i in range(100, 200)]
    ant_labels = ['A' + str(i) for i in range(131, 147)]

    robot_list = [Spyder(label) for label in spyder_labels]
    robot_list += [Ladder(label) for label in ladder_labels]
    robot_list += [Ant(label) for label in ant_labels]

    helper = Helper(robot_list=robot_list)
    helper.log.info(args)

    mqtt_client = MQTTClient(callback=helper.mqtt_receive_callback)
    mqtt_client.start(host=args.server_ip, port=args.server_port,
                      username=args.username, password=args.password)

    for r in robot_list:
        mqtt_client.add_robot(r.robot_label)

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        mqtt_client.stop()


if __name__ == "__main__":
    main(parse_args())
