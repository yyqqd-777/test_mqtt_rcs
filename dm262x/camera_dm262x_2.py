import math
import time
import socket
from loguru import logger


dm_code = "0000000120000104;384,451;744,459;761,93;386,81;"


# 相机通信地址
host = "192.168.100.100"
port = 23

# 四个点
POINT_A = 0
POINT_B = 1
POINT_C = 2
POINT_D = 3

# 分辨率最大值 X
MAX_DPI_X = 1280
# 分辨率最大值 Y
MAX_DPI_Y = 960
# DM 二维码物理尺寸
DM_CODE_SIZE_MM = 22.5


def calc_abc_from_line_2d(x0, y0, x1, y1):
    """ 通过两个坐标点计算出直线一般式的系数, Ax + By + C = 0 """
    a = y0 - y1
    b = x1 - x0
    c = x0 * y1 - x1 * y0
    return a, b, c


def get_line_cross_point(line1, line2):
    a0, b0, c0 = calc_abc_from_line_2d(*line1)
    a1, b1, c1 = calc_abc_from_line_2d(*line2)
    d = a0 * b1 - a1 * b0
    if d == 0:
        # 两条线平行, 没有交点
        return None
    x = (b0 * c1 - b1 * c0) / d
    y = (a1 * c0 - a0 * c1) / d
    return x, y


def unpack_data(scan_data):
    """ 解包数据
        # 解包数据1 0000000120000104;428,539;682,542;687,283;428,283;
        # code 0000000120000104
        # XY1 428,539
        # XY2 682,542
        # XY3 687,283
        # XY4 428,283
        # 解包数据2 0005000120000204;941,403;720,184;497,409;721,627;
        # code 0005000120000204
        # XY1 941,403
        # XY2 720,184
        # XY3 497,409
        # XY4 721,627
    """
    parsed_data = scan_data.strip('()').split(';')
    code = parsed_data[0]

    point = {}
    for i in range(1, 5):
        point[i - 1] = parsed_data[i]

    x_camera = {}
    y_camera = {}
    for i in range(4):
        parsed_point = point[i].split(',')
        x_camera[i] = float(parsed_point[0])
        y_camera[i] = float(parsed_point[1])

    return code, x_camera, y_camera


def coord_convert(x_camera, y_camera):
    """ 将相机的坐标系转换成常规理解的直角坐标系
        # 使相机坐标系和常规理解坐标系的 X+ 对齐
        # 同时将坐标系的原点移动到相机中心
        #
        # 相机使用的直角坐标系:
        #   X+ 方向顺时针旋转 90 度等于 Y+ 方向
        # 常规理解的直角坐标系:
        #   X+ 方向逆时针旋转 90 度等于 Y+ 方向
    """
    x = {}
    y = {}
    for i in range(4):
        x[i] = x_camera[i] - (MAX_DPI_X / 2)
        y[i] = (MAX_DPI_Y / 2) - y_camera[i]

    return x, y


def fx_coord(x, y):
    """ 解码坐标数据
        # 将二维码的四个像素坐标转换成物理偏移及角偏移
        #
        ## 计算二维码的斜率
        ## 计算像素点的物理值, mm/dpi
        ## 计算二维码中心的像素坐标
        ## 将二维码中心的像素坐标转换成物理坐标
        ## 返回退出
        ##
    """
    # 计算边 ab 和边 ad 的斜率
    rad_ab = math.atan2((y[POINT_B] - y[POINT_A]), (x[POINT_B] - x[POINT_A]))
    rad_ad = math.atan2((y[POINT_D] - y[POINT_A]), (x[POINT_D] - x[POINT_A]))

    # 计算边 ab 和边 ad 在 x 轴上的投影距离
    # 计算二维码 a 点与 b 点在像素坐标 x 轴中的投影距离
    dm_code_ab_dpi_dx = x[POINT_B] - x[POINT_A]
    # 计算二维码 a 点与 d 点在像素坐标 x 轴中的投影距离
    dm_code_ad_dpi_dx = x[POINT_D] - x[POINT_A]

    # 计算二维码 a 点与 b 点在像素坐标 y 轴中的投影距离
    dm_code_ab_dpi_dy = y[POINT_B] - y[POINT_A]
    # 计算二维码 a 点与 d 点在像素坐标 y 轴中的投影距离
    dm_code_ad_dpi_dy = y[POINT_D] - y[POINT_A]

    # 选出 x 轴的投影距离大的线段, 这个做法能提高计算精度及规避后续计算除数为 0 的可能
    if abs(dm_code_ab_dpi_dx) > abs(dm_code_ad_dpi_dx):
        # 边 ab 的 x 轴投影比边 ad 的 x 轴投影长, 我们选边 ab
        dm_code_mm_dx = DM_CODE_SIZE_MM * math.cos(rad_ab)
        dpi_1x1_x = dm_code_mm_dx / dm_code_ab_dpi_dx
    else:
        # 边 ab 的 x 轴投影比边 ad 的 x 轴投影短, 我们选边 ad
        dm_code_mm_dx = DM_CODE_SIZE_MM * math.cos(rad_ad)
        dpi_1x1_x = dm_code_mm_dx / dm_code_ad_dpi_dx

    # 选出 y 轴的投影距离大的线段, 这个做法能提高计算精度及规避后续计算除数为 0 的可能
    if abs(dm_code_ab_dpi_dy) > abs(dm_code_ad_dpi_dy):
        # 边 ab 的 y 轴投影比边 ad 的 y 轴投影长, 我们选边 ab
        dm_code_mm_y = DM_CODE_SIZE_MM * math.sin(rad_ab)
        dpi_1x1_y = dm_code_mm_y / dm_code_ab_dpi_dy
    else:
        # 边 ab 的 y 轴投影比边 ad 的 y 轴投影短, 我们选边 ad
        dm_code_mm_y = DM_CODE_SIZE_MM * math.sin(rad_ad)
        dpi_1x1_y = dm_code_mm_y / dm_code_ad_dpi_dy

    # 计算出二维码中心的像素坐标
    dm_code_coord = get_line_cross_point(
        (x[POINT_A], y[POINT_A], x[POINT_C], y[POINT_C]), (x[POINT_B], y[POINT_B], x[POINT_D], y[POINT_D]))
    if dm_code_coord == None:
        logger.error(
            "error: Failed to calculate the center point of the two-dimensional code.")
        return
    point_x, point_y = dm_code_coord

    # 将二维码中心的像素坐标转换成物理坐标
    point_x_mm = point_x * dpi_1x1_x
    point_y_mm = point_y * dpi_1x1_y

    # 返回退出
    x_office = point_x_mm
    y_office = point_y_mm
    theta = rad_ab
    return x_office, y_office, theta


def main():

    logger.info("start...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        while True:
            # 获取相机数据
            data = s.recv(1024)
            data = data.decode("utf-8")
            logger.info(f"...0... {data}")

            # 如果相机数据无效则执行下一次读码, 否则解析数据并打印
            if (data == '(noread)'):
                continue
            else:
                code, x_camera, y_camera = unpack_data(data)
                x, y = coord_convert(x_camera, y_camera)
                x_office, y_office, theta = fx_coord(x, y)

                logger.info(f"...1... {code}")
                logger.info(f"...2... theta =  {theta:.4f} rad.")
                logger.info(f"...3... x_office = {x_office} mm.")
                logger.info(f"...4... y_office = {y_office} mm.")


if __name__ == '__main__':
    main()
