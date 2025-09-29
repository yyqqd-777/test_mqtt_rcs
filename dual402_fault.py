# 截取自机器人日志文件
# [00:22:06.372,000] <dbg> dual402: start: _traj_1.planTrapezoidal: 1243445 268089 -107 320000 160000 160000
# [00:22:06.372,000] <dbg> dual402: start: _traj_2.planTrapezoidal: 1243445 268064 -2527 320000 160000 160000
# ...
# [00:22:07.676,000] <err> dual402: 1.080000 352130 349599 -6871 -10042 361285 358646 2639
# [00:22:08.616,000] <err> dual402: 2.020000 576931 572115 223141 217695 594275 589390 4885


import math


def sign_hard(val):
    return -1.0 if math.copysign(1, val) < 0 else 1.0


def sq(x):
    return x * x


class Step:
    def __init__(self, Y=0.0, Yd=0.0, Ydd=0.0):
        self.Y = Y
        self.Yd = Yd
        self.Ydd = Ydd

    def __repr__(self) -> str:
        return f"Step(Y={self.Y}, Yd={self.Yd}, Ydd={self.Ydd})"


class TrapezoidalTrajectory:
    def __init__(self):
        self.Xi_ = 0.0
        self.Xf_ = 0.0
        self.Vi_ = 0.0
        self.Vmax_ = 0.0
        self.Ar_ = 0.0
        self.Dr_ = 0.0
        self.Vr_ = 0.0
        self.Ta_ = 0.0
        self.Tv_ = 0.0
        self.Td_ = 0.0
        self.Tf_ = 0.0
        self.yAccel_ = 0.0

    def __repr__(self) -> str:
        return (
            f"TrapezoidalTrajectory(\n"
            f"  Xi = {self.Xi_}, Xf = {self.Xf_},\n"
            f"  Vi = {self.Vi_}, Vmax = {self.Vmax_},\n"
            f"  Ar = {self.Ar_}, Vr = {self.Vr_}, Dr = {self.Dr_},\n"
            f"  Ta = {self.Ta_}, Tv = {self.Tv_}, Td = {self.Td_},\n"
            f"  Tf = {self.Tf_}, yAccel = {self.yAccel_}\n"
            f")"
        )

    def plan_trapezoidal(self, Xf, Xi, Vi, Vmax, Amax, Dmax):
        dX = Xf - Xi  # Distance to travel
        stop_dist = (Vi * Vi) / (2.0 * Dmax)  # Minimum stopping distance
        dXstop = math.copysign(stop_dist, Vi)  # Minimum stopping displacement
        s = sign_hard(dX - dXstop)  # Sign of coast velocity (if any)
        self.Ar_ = s * Amax  # Maximum Acceleration (signed)
        self.Dr_ = -s * Dmax  # Maximum Deceleration (signed)
        self.Vr_ = s * Vmax  # Maximum Velocity (signed)

        # If we start with a speed faster than cruising, then we need to decel instead of accel
        if (s * Vi) > (s * self.Vr_):
            self.Ar_ = -s * Amax

        # Time to accel/decel to/from Vr (cruise speed)
        self.Ta_ = (self.Vr_ - Vi) / self.Ar_
        self.Td_ = -self.Vr_ / self.Dr_

        # Minimum displacement required to reach cruising speed
        dXmin = 0.5 * self.Ta_ * (self.Vr_ + Vi) + 0.5 * self.Td_ * self.Vr_

        # Are we displacing enough to reach cruising speed?
        if s * dX < s * dXmin:
            # Short move (triangle profile)
            self.Vr_ = s * math.sqrt(max((self.Dr_ * sq(Vi) + 2 *
                                     self.Ar_ * self.Dr_ * dX) / (self.Dr_ - self.Ar_), 0.0))
            self.Ta_ = max(0.0, (self.Vr_ - Vi) / self.Ar_)
            self.Td_ = max(0.0, -self.Vr_ / self.Dr_)
            self.Tv_ = 0.0
        else:
            # Long move (trapezoidal profile)
            self.Tv_ = (dX - dXmin) / self.Vr_

        # Fill in the rest of the values used at evaluation-time
        self.Tf_ = self.Ta_ + self.Tv_ + self.Td_
        self.Xi_ = Xi
        self.Xf_ = Xf
        self.Vi_ = Vi
        self.Vmax_ = Vmax
        self.yAccel_ = Xi + Vi * self.Ta_ + 0.5 * self.Ar_ * sq(self.Ta_)

        return True

    def eval(self, t):
        trajStep = Step()
        if t < 0.0:
            # Initial Condition
            trajStep.Y = self.Xi_
            trajStep.Yd = self.Vi_
            trajStep.Ydd = 0.0
        elif t < self.Ta_:
            # Accelerating
            trajStep.Y = self.Xi_ + self.Vi_ * t + 0.5 * self.Ar_ * sq(t)
            trajStep.Yd = self.Vi_ + self.Ar_ * t
            trajStep.Ydd = self.Ar_
        elif t < self.Ta_ + self.Tv_:
            # Coasting
            trajStep.Y = self.yAccel_ + self.Vr_ * (t - self.Ta_)
            trajStep.Yd = self.Vr_
            trajStep.Ydd = 0.0
        elif t < self.Tf_:
            # Deceleration
            td = t - self.Tf_
            trajStep.Y = self.Xf_ + 0.5 * self.Dr_ * sq(td)
            trajStep.Yd = self.Dr_ * td
            trajStep.Ydd = self.Dr_
        elif t >= self.Tf_:
            # Final Condition
            trajStep.Y = self.Xf_
            trajStep.Yd = 0.0
            trajStep.Ydd = 0.0
        else:
            # Error condition, could raise an exception or log an error
            pass

        return trajStep


# Plan the trapezoidal trajectory
t1 = TrapezoidalTrajectory()
t2 = TrapezoidalTrajectory()
t1.plan_trapezoidal(1243445, 268089, -107, 320000, 160000, 160000)
t2.plan_trapezoidal(1243445, 268064, -2527, 320000, 160000, 160000)
print(t1)
print(t2)

# Evaluate the trajectory at a specific time
# 取机器人日志中的值进行验算，结果一致
# 推测原因，蜘蛛在规划运动路径时，由于梯子正在快速运行，即使蜘蛛处于静止状态，两个电机反馈的实际速度仍较大，导致规划曲线同步出现问题
tdc = 1.080000
result_1 = t1.eval(tdc)
result_2 = t2.eval(tdc)
print("=" * 50)
print(f"tdc = {tdc}s")
print(f"step1 = {result_1}")
print(f"step2 = {result_2}")
print(f"target differ: {result_1.Y - result_2.Y}")

tdc = 2.020000
result_1 = t1.eval(tdc)
result_2 = t2.eval(tdc)
print("=" * 50)
print(f"tdc = {tdc}s")
print(f"step1 = {result_1}")
print(f"step2 = {result_2}")
print(f"target differ: {result_1.Y - result_2.Y}")
