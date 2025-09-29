import math


class DoubleDiff402:

    def _position_to_millimeter(slef, position):
        millimeter = position / 90000 * math.pi * 150.00
        return millimeter

    def _angle_diff_calculate(self, target_theta, current_theta):
        delta_theta = target_theta - current_theta

        # 将 delta_theta 归一化到 [-π, π)
        delta_theta = math.fmod(delta_theta + 3*math.pi,
                                2.0 * math.pi) - math.pi

        return delta_theta

    def _get_left_distance(self, start_x, start_y, end_x, end_y, move_x, move_y):
        vector_se_x = end_x - start_x
        vector_se_y = end_y - start_y

        se_length = math.sqrt(math.pow(vector_se_x, 2) +
                              math.pow(vector_se_y, 2))

        # 计算 (move_x, move_y) 投影点 (move_xx, move_yy)
        vector_sm_x = move_x - start_x
        vector_sm_y = move_y - start_y

        dot_product = (vector_sm_x * vector_se_x) + (vector_sm_y * vector_se_y)

        projection_factor = dot_product / \
            (math.pow(vector_se_x, 2) + math.pow(vector_se_y, 2))

        move_xx = start_x + projection_factor * vector_se_x
        move_yy = start_y + projection_factor * vector_se_y

        sm_length = math.sqrt(
            math.pow(move_xx - start_x, 2) + math.pow(move_yy - start_y, 2))
        em_length = math.sqrt(
            math.pow(move_xx - end_x, 2) + math.pow(move_yy - end_y, 2))

        if em_length > se_length:
            return em_length

        return se_length - sm_length


# 示例调用
print(math.pi)
diff_calculator = DoubleDiff402()
result = diff_calculator._get_left_distance(
    109000, 115000, 109000, 102000, 109000, 101990.5343)
print(result)

print("_angle_diff_calculate")
print("逆时针转 正数")

result = diff_calculator._angle_diff_calculate(-3.14, 3.14)
print(result)

result = diff_calculator._angle_diff_calculate(-3.14, -3.1415)
print(result)

result = diff_calculator._angle_diff_calculate(1, -1.15)
print(result)

result = diff_calculator._angle_diff_calculate(3.14, 1.57)
print(result)

print("顺时针转 负数")
result = diff_calculator._angle_diff_calculate(3.14, -3.14)
print(result)

result = diff_calculator._angle_diff_calculate(-3.1415, -3.14)
print(result)

result = diff_calculator._angle_diff_calculate(-1, 1.15)
print(result)

result = diff_calculator._angle_diff_calculate(1.57, 3.14)
print(result)


def adjust_range(value):
    return math.fmod(value + 3*2048.0, 4096.0) - 2048.0


# 测试
test_values = [-4095, -2048, 0, 2047, 4095]

for value in test_values:
    adjusted_value = adjust_range(value)
    print(f"Original: {value}, Adjusted: {adjusted_value}")

# linear -> current_x: 100996.200000, current_y:102001.300000
# stopped -> current_x: 105997.213660, current_y: 101998.677208

point1 = (100996.200000, 102001.300000)
point2 = (105997.213660, 101998.677208)

# 计算欧几里得距离
distance = math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

diff = 1112696576 - 1111751936
result = diff_calculator._position_to_millimeter(diff)
print(f"distance: {distance} result: {result}mm")


# linear -> moto1_pos:-1111559808,  motor2_pos:911324736
# linear -> current_x: 100003.500000, current_y:102006.400000.
# stopped -> current_x: 100996.095186, current_y: 102001.200067,
# linear -> moto1_pos:-1111559808,  motor2_pos:911324736
# moto1_pos:-1111751936,  motor2_pos:911512000

point1 = (103700, 101000)
point2 = (103700, 100000)

distance = math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
diff = 2031945344 - 2031747200
result = diff_calculator._position_to_millimeter(diff)
print(f"distance: {distance} result: {result}mm")
