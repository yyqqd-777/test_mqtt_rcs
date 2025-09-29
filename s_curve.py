import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve


class SCurveConstraints:
    def __init__(self, max_jerk, max_acceleration, max_velocity):
        self.max_jerk = max_jerk
        self.max_acceleration = max_acceleration
        self.max_velocity = max_velocity


class SCurveTimeIntervals:
    def __init__(self, t_j1=0, t_j2=0, t_a=0, t_v=0, t_d=0):
        self.t_j1 = t_j1
        self.t_j2 = t_j2
        self.t_a = t_a
        self.t_v = t_v
        self.t_d = t_d

    def total_duration(self):
        return self.t_a + self.t_d + self.t_v

    def is_max_acceleration_not_reached(self):
        return self.t_a < 2.0 * self.t_j1 or self.t_d < 2.0 * self.t_j2


class SCurveStartConditions:
    def __init__(self, q0=0.0, q1=1.0, v0=0.0, v1=0.0):
        self.q0 = q0
        self.q1 = q1
        self.v0 = v0
        self.v1 = v1

    def h(self):
        return abs(self.q1 - self.q0)

    def dir(self):
        return -1.0 if self.q1 < self.q0 else 1.0


class SCurveParameters:
    def __init__(self, time_intervals, constraints, start_conditions):
        self.time_intervals = time_intervals
        self.j_max = constraints.max_jerk
        self.j_min = -constraints.max_jerk
        self.a_lim_a = constraints.max_jerk * time_intervals.t_j1
        self.a_lim_d = -constraints.max_jerk * time_intervals.t_j2
        self.v_lim = start_conditions.dir() * start_conditions.v0 + \
            (time_intervals.t_a - time_intervals.t_j1) * self.a_lim_a
        self.conditions = start_conditions


class SCurveInput:
    def __init__(self, constraints, start_conditions):
        self.constraints = constraints
        self.start_conditions = start_conditions

    def calc_intervals(self):
        return self.calc_times_case_1()

    def is_trajectory_feasible(self):
        t_j_star = min(
            np.sqrt(abs(self.start_conditions.v1 -
                    self.start_conditions.v0) / self.constraints.max_jerk),
            self.constraints.max_acceleration / self.constraints.max_jerk,
        )
        if abs(t_j_star - self.constraints.max_acceleration / self.constraints.max_jerk) < 1e-10:
            return self.start_conditions.h() > 0.5 * (self.start_conditions.v1 + self.start_conditions.v0) * (t_j_star + abs(self.start_conditions.v1 - self.start_conditions.v0) / self.constraints.max_acceleration)
        if t_j_star < self.constraints.max_acceleration / self.constraints.max_jerk:
            return self.start_conditions.h() > t_j_star * (self.start_conditions.v0 + self.start_conditions.v1)
        return False

    def is_a_max_not_reached(self):
        return (self.constraints.max_velocity - self.start_conditions.v0) * self.constraints.max_jerk < self.constraints.max_acceleration ** 2

    def is_a_min_not_reached(self):
        return (self.constraints.max_velocity - self.start_conditions.v1) * self.constraints.max_jerk < self.constraints.max_acceleration ** 2

    def calc_times_case_1(self):
        times = SCurveTimeIntervals()
        new_input = SCurveInput(self.constraints, self.start_conditions)
        dir = self.start_conditions.dir()
        if self.is_a_max_not_reached():
            times.t_j1 = np.sqrt((new_input.constraints.max_velocity -
                                 self.start_conditions.v0) / new_input.constraints.max_jerk)
            times.t_a = 2.0 * times.t_j1
        else:
            times.t_j1 = new_input.constraints.max_acceleration / new_input.constraints.max_jerk
            times.t_a = times.t_j1 + (new_input.constraints.max_velocity - dir *
                                      self.start_conditions.v0) / new_input.constraints.max_acceleration

        if self.is_a_min_not_reached():
            times.t_j2 = np.sqrt((new_input.constraints.max_velocity -
                                 self.start_conditions.v1) / new_input.constraints.max_jerk)
            times.t_d = 2.0 * times.t_j2
        else:
            times.t_j2 = new_input.constraints.max_acceleration / new_input.constraints.max_jerk
            times.t_d = times.t_j2 + (new_input.constraints.max_velocity - dir *
                                      self.start_conditions.v1) / new_input.constraints.max_acceleration

        times.t_v = self.start_conditions.h() / new_input.constraints.max_velocity - times.t_a / 2.0 * (1.0 + dir * self.start_conditions.v0 /
                                                                                                        new_input.constraints.max_velocity) - times.t_d / 2.0 * (1.0 + dir * self.start_conditions.v1 / new_input.constraints.max_velocity)
        if times.t_v <= 0.0:
            return self.calc_times_case_2(0)
        if times.is_max_acceleration_not_reached():
            new_input.constraints.max_acceleration *= 0.5
            if new_input.constraints.max_acceleration > 0.01:
                return new_input.calc_times_case_2(0)
            new_input.constraints.max_acceleration = 0.0
        self.handle_negative_acceleration_time(times, new_input)
        return times

    def calc_times_case_2(self, recursion_depth):
        recursion_depth += 1
        times = self.get_times_case_2()
        new_input = SCurveInput(self.constraints, self.start_conditions)
        if times.is_max_acceleration_not_reached():
            new_input.constraints.max_acceleration *= 0.5
            if new_input.constraints.max_acceleration > 0.01:
                return new_input.calc_times_case_2(recursion_depth)
            new_input.constraints.max_acceleration = 0.0
        self.handle_negative_acceleration_time(times, new_input)
        if recursion_depth != 1:
            new_input.constraints.max_acceleration *= 2.0
        new_input.calc_times_case_2_precise(recursion_depth)
        return times

    def get_times_case_2(self):
        t_j1 = self.constraints.max_acceleration / self.constraints.max_jerk
        t_j2 = self.constraints.max_acceleration / self.constraints.max_jerk
        delta = self.constraints.max_acceleration ** 4 / self.constraints.max_jerk ** 2 + 2.0 * (self.start_conditions.v0 ** 2 + self.start_conditions.v1 ** 2) + self.constraints.max_acceleration * (
            4.0 * self.start_conditions.h() - 2.0 * self.constraints.max_acceleration / self.constraints.max_jerk * (self.start_conditions.v0 + self.start_conditions.v1))
        t_a = (self.constraints.max_acceleration ** 2 / self.constraints.max_jerk - 2.0 *
               self.start_conditions.v0 + np.sqrt(delta)) / (2.0 * self.constraints.max_acceleration)
        t_d = (self.constraints.max_acceleration ** 2 / self.constraints.max_jerk - 2.0 *
               self.start_conditions.v1 + np.sqrt(delta)) / (2.0 * self.constraints.max_acceleration)
        t_v = 0.0
        return SCurveTimeIntervals(t_j1, t_j2, t_a, t_v, t_d)

    def calc_times_case_2_precise(self, recursion_depth):
        recursion_depth += 1
        times = self.get_times_case_2()
        new_input = SCurveInput(self.constraints, self.start_conditions)
        if times.is_max_acceleration_not_reached():
            new_input.constraints.max_acceleration *= 0.99
            if new_input.constraints.max_acceleration > 0.01:
                return new_input.calc_times_case_2_precise(recursion_depth)
            new_input.constraints.max_acceleration = 0.0
        self.handle_negative_acceleration_time(times, new_input)
        return times

    def handle_negative_acceleration_time(self, times, new_input):
        if times.t_a < 0.0:
            times.t_j1 = 0.0
            times.t_a = 0.0
            times.t_d = 2.0 * self.start_conditions.h() / (self.start_conditions.v0 +
                                                           self.start_conditions.v1)
            times.t_j2 = (new_input.constraints.max_jerk * self.start_conditions.h() - np.sqrt(new_input.constraints.max_jerk * (new_input.constraints.max_jerk * self.start_conditions.h() ** 2 + (
                self.start_conditions.v0 + self.start_conditions.v1) ** 2 * (self.start_conditions.v1 - self.start_conditions.v0)))) / (new_input.constraints.max_jerk * (self.start_conditions.v1 + self.start_conditions.v0))
        if times.t_d < 0.0:
            times.t_j2 = 0.0
            times.t_d = 0.0
            times.t_a = 2.0 * self.start_conditions.h() / (self.start_conditions.v0 +
                                                           self.start_conditions.v1)
            times.t_j2 = (new_input.constraints.max_jerk * self.start_conditions.h() - np.sqrt(new_input.constraints.max_jerk * (new_input.constraints.max_jerk * self.start_conditions.h() ** 2 - (
                self.start_conditions.v0 + self.start_conditions.v1) ** 2 * (self.start_conditions.v1 - self.start_conditions.v0)))) / (new_input.constraints.max_jerk * (self.start_conditions.v1 + self.start_conditions.v0))


def eval_position(p, t):
    times = p.time_intervals
    if t < 0.0:
        return p.conditions.q0
    dir = p.conditions.dir()
    if t <= times.t_j1:
        return p.conditions.q0 + p.conditions.v0 * t + dir * p.j_max * t ** 3 / 6.0
    elif t <= times.t_a - times.t_j1:
        return p.conditions.q0 + p.conditions.v0 * t + dir * p.a_lim_a / 6.0 * (3.0 * t ** 2 - 3.0 * times.t_j1 * t + times.t_j1 ** 2)
    elif t <= times.t_a:
        return p.conditions.q0 + dir * (p.v_lim + dir * p.conditions.v0) * times.t_a / 2.0 - dir * p.v_lim * (times.t_a - t) - dir * p.j_min * (times.t_a - t) ** 3 / 6.0
    elif t <= times.t_a + times.t_v:
        return p.conditions.q0 + dir * (p.v_lim + dir * p.conditions.v0) * times.t_a / 2.0 + dir * p.v_lim * (t - times.t_a)
    elif t <= times.total_duration() - times.t_d + times.t_j2:
        return p.conditions.q1 - dir * (p.v_lim + dir * p.conditions.v1) * times.t_d / 2.0 + dir * p.v_lim * (t - times.total_duration() + times.t_d) - dir * p.j_max * (t - times.total_duration() + times.t_d) ** 3 / 6.0
    elif t <= times.total_duration() - times.t_j2:
        return p.conditions.q1 - dir * (p.v_lim + dir * p.conditions.v1) * times.t_d / 2.0 + dir * p.v_lim * (t - times.total_duration() + times.t_d) + dir * p.a_lim_d / 6.0 * (3.0 * (t - times.total_duration() + times.t_d) ** 2 - 3.0 * times.t_j2 * (t - times.total_duration() + times.t_d) + times.t_j2 ** 2)
    elif t <= times.total_duration():
        return p.conditions.q1 - p.conditions.v1 * (times.total_duration() - t) - dir * p.j_max * (times.total_duration() - t) ** 3 / 6.0
    else:
        return p.conditions.q1


def eval_velocity(p, t):
    times = p.time_intervals
    if t < 0.0:
        return p.conditions.v0
    dir = p.conditions.dir()
    if t <= times.t_j1:
        return p.conditions.v0 + dir * p.j_max * t ** 2 / 2.0
    elif t <= times.t_a - times.t_j1:
        return p.conditions.v0 + dir * p.a_lim_a * (t - times.t_j1 / 2.0)
    elif t <= times.t_a:
        return dir * p.v_lim + dir * p.j_min * (times.t_a - t) ** 2 / 2.0
    elif t <= times.t_a + times.t_v:
        return dir * p.v_lim
    elif t <= times.total_duration() - times.t_d + times.t_j2:
        return dir * p.v_lim - dir * p.j_max * (t - times.total_duration() + times.t_d) ** 2 / 2.0
    elif t <= times.total_duration() - times.t_j2:
        return dir * p.v_lim + dir * p.a_lim_d * (t - times.total_duration() + times.t_d - times.t_j2 / 2.0)
    elif t <= times.total_duration():
        return p.conditions.v1 + dir * p.j_max * (times.total_duration() - t) ** 2 / 2.0
    else:
        return p.conditions.v1


def eval_acceleration(p, t):
    times = p.time_intervals
    dir = p.conditions.dir()
    if t < 0.0:
        return 0.0
    elif t <= times.t_j1:
        return dir * p.j_max * t
    elif t <= times.t_a - times.t_j1:
        return dir * p.a_lim_a
    elif t <= times.t_a:
        return dir * (-p.j_min) * (times.t_a - t)
    elif t <= times.t_a + times.t_v:
        return 0.0
    elif t <= times.total_duration() - times.t_d + times.t_j2:
        return dir * (-p.j_max) * (t - times.total_duration() + times.t_d)
    elif t <= times.total_duration() - times.t_j2:
        return dir * p.a_lim_d
    elif t <= times.total_duration():
        return dir * (-p.j_max) * (times.total_duration() - t)
    else:
        return 0.0


def eval_jerk(p, t):
    times = p.time_intervals
    dir = p.conditions.dir()
    if t < times.t_j1:
        return dir * p.j_max
    elif t <= times.t_a - times.t_j1:
        return 0.0
    elif t <= times.t_a:
        return dir * p.j_min
    elif t <= times.t_a + times.t_v:
        return 0.0
    elif t <= times.total_duration() - times.t_d + times.t_j2:
        return dir * p.j_min
    elif t <= times.total_duration() - times.t_j2:
        return 0.0
    else:
        return dir * p.j_max


def s_curve_generator(input_parameters, derivative):
    times = input_parameters.calc_intervals()
    params = SCurveParameters(
        times, input_parameters.constraints, input_parameters.start_conditions)
    if derivative == 'Position':
        return params, lambda t: eval_position(params, t)
    elif derivative == 'Velocity':
        return params, lambda t: eval_velocity(params, t)
    elif derivative == 'Acceleration':
        return params, lambda t: eval_acceleration(params, t)
    elif derivative == 'Jerk':
        return params, lambda t: eval_jerk(params, t)
    else:
        raise ValueError("Invalid derivative type")


# Example usage
constraints = SCurveConstraints(
    max_jerk=3.0, max_acceleration=2.0, max_velocity=2.0)
start_conditions = SCurveStartConditions(q0=0.0, q1=5.0, v0=0.0, v1=0.0)
input_parameters = SCurveInput(constraints, start_conditions)

# Plotting the results
derivatives = ['Jerk', 'Position', 'Velocity', 'Acceleration']

# Initialize plot
fig, ax = plt.subplots()
ax.set_title('S-Curve Velocity Motion Profile')
ax.set_xlabel('time in seconds')
ax.set_ylabel('Position derivatives m, m/s, m/s², m/s³')

# Colors for different derivatives
colors = {'Position': 'blue', 'Velocity': 'green',
          'Acceleration': 'red', 'Jerk': 'orange'}

# Generate curves for each derivative and plot
for derivative in derivatives:
    params, s_curve = s_curve_generator(input_parameters, derivative)
    time = np.linspace(0, params.time_intervals.total_duration(), 1001)
    y = np.array([s_curve(t) for t in time])
    ax.plot(time, y, label=derivative, color=colors[derivative])

# Show legend
ax.legend()

# Display plot
plt.legend()
plt.grid(True)
plt.show()
