import socket
import datetime


def connect_to_server(ip, port):
    try:
        # 创建一个Socket对象
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 设置超时时间（可选）
        client_socket.settimeout(20)

        print(f"Connecting to {ip}:{port}...")

        # 尝试连接服务器
        client_socket.connect((ip, port))
        print("Connected to the server successfully!")

        while True:
            try:
                # 接收数据（缓冲区大小为1024字节）
                data = client_socket.recv(1024)
                if not data:
                    print("Connection closed by the server.")
                    break
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"{timestamp} Received: {data.decode('utf-8')}")
            except socket.timeout:
                print("No data received: connection timed out.")
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
    except socket.timeout:
        print("Connection attempt timed out.")
    except ConnectionRefusedError:
        print("Connection refused by the server.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # 确保关闭Socket

        client_socket.close()
        print("Connection closed.")


if __name__ == "__main__":
    # 设置目标IP和端口
    target_ip = "192.168.100.100"
    target_port = 23

    # target_ip = "192.168.100.101"
    # target_port = 3000

    connect_to_server(target_ip, target_port)
