import numpy as np
import matplotlib.pyplot as plt
import mplcursors


def sign_hard(val):
    return -1.0 if val < 0 else 1.0


class PlanParameters:
    def __init__(self, Xi=0.0, Xf=0.0, Vi=0.0, Vf=0.0, Vmax=2.0, Amax=0.5, Dmax=0.5):
        self._Xi = Xi
        self._Xf = Xf
        self._Vi = Vi
        self._Vf = Vf
        self._Vmax = Vmax
        self._Amax = Amax
        self._Dmax = Dmax

    def __str__(self):
        return f"Xi = {self._Xi} Xf = {self._Xf} Vi = {self._Vi} Vf = {self._Vf} Vmax = {self._Vmax} Amax = {self._Amax} Dmax = {self._Dmax}"


class TrapezoidalTrajectory:
    class Step:
        def __init__(self, Y=0.0, Yd=0.0, Ydd=0.0):
            self.Y = Y
            self.Yd = Yd
            self.Ydd = Ydd

    def __init__(self):
        self.Ar_ = 0.0
        self.Dr_ = 0.0
        self.Vr_ = 0.0
        self.Ta_ = 0.0
        self.Td_ = 0.0
        self.Tv_ = 0.0
        self.Tf_ = 0.0
        self.Xi_ = 0.0
        self.Xf_ = 0.0
        self.Vi_ = 0.0
        self.Vmax_ = 0.0
        self.yAccel_ = 0.0

        # S-curve profile variables
        self.AJa_ = 0.0
        self.AUa_ = 0.0
        self.ANa_ = 0.0
        self.TAja_ = 0.0
        self.TAua_ = 0.0
        self.TAna_ = 0.0

        self.DJa_ = 0.0
        self.DUa_ = 0.0
        self.DNa_ = 0.0
        self.TDja_ = 0.0
        self.TDua_ = 0.0
        self.TDna_ = 0.0

        self.Tsa_ = 0.0
        self.Tsd_ = 0.0
        self.Tsv_ = 0.0
        self.Tsf_ = 0.0

    def calc_Tsv(self, Vr, Tsa, Tsd):
        return (
            self.Xf_
            - self.Xi_
            - self.Vi_ * Tsa
            - 0.5 * Tsa * (Vr - self.Vi_)
            - 0.5 * Tsd * (Vr - self.Vf_)
            - self.Vf_ * Tsd
        ) / Vr

    def plan_scurve_original(self, Xf, Xi, Vi, Vf, Vmax, Amax, Dmax) -> bool:

        # 为了加速/减速过程与梯形的时间一致，规划梯形时最大加/减速减版
        self.plan_trapezoidal_original(
            Xf, Xi, Vi, Vf, Vmax, Amax / 2, Dmax / 2)

        k = 2.0
        i = 2.0

        if self.Ta_ > 0.0:
            j = k / self.Ta_ * 2 * i
            (
                self.AJa_,
                self.AUa_,
                self.ANa_,
                self.TAja_,
                self.TAua_,
                self.TAna_,
            ) = self._velocityTrapezoidal(
                self.Vr_, self.Vi_, k * self.Ar_, j * self.Ar_, j * self.Ar_
            )
        else:
            (
                self.AJa_,
                self.AUa_,
                self.ANa_,
                self.TAja_,
                self.TAua_,
                self.TAna_,
            ) = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        if self.Td_ > 0.0:
            z = k / self.Td_ * 2 * i
            (
                self.DJa_,
                self.DUa_,
                self.DNa_,
                self.TDja_,
                self.TDua_,
                self.TDna_,
            ) = self._velocityTrapezoidal(
                self.Vf_,
                self.Vr_,
                k * self.Dr_ * -1,
                z * self.Dr_ * -1,
                z * self.Dr_ * -1,
            )
        else:
            (
                self.DJa_,
                self.DUa_,
                self.DNa_,
                self.TDja_,
                self.TDua_,
                self.TDna_,
            ) = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        # print(
        #     f"self.TAja_ {self.TAja_} self.TAua {self.TAua_}  self.TAna_ {self.TAna_}"
        # )
        # print(
        #     f"self.TDja_ {self.TDja_} self.TDua {self.TDua_}  self.TDna_ {self.TDna_}"
        # )

        print(f"self.AJa_ {self.AJa_} self.AUa_ {
              self.AUa_}  self.ANa_ {self.ANa_}")

        print(f"self.DJa_ {self.DJa_} self.DUa_ {
              self.DUa_}  self.DNa_ {self.DNa_}")

        self.Tsa_ = self.TAja_ + self.TAua_ + self.TAna_
        self.Tsd_ = self.TDja_ + self.TDua_ + self.TDna_

        # 匀速时间 = （总距离 - S加速距离 - S加速距离）/ 匀速度
        self.Tsv_ = self.calc_Tsv(self.Vr_, self.Tsa_, self.Tsd_)

        print(f"self.Vr_ {self.Vr_} Tsv_ {self.Tsv_} Vmax_ {self.Vmax_}")

        new_Vr = self.Vr_
        new_Tsv = self.Tsv_
        while new_Tsv > 0.0 and abs(new_Vr) < self.Vmax_:
            new_Vr *= 1.01
            if abs(new_Vr) >= self.Vmax_:
                new_Vr = sign_hard(self.Vr_) * self.Vmax_

            new_TAua = self.TAua_ + (new_Vr - self.Vr_) / self.AUa_
            new_TDua = self.TDua_ + (self.Vr_ - new_Vr) / self.DUa_

            new_Tsv = self.calc_Tsv(
                new_Vr, self.TAja_ + new_TAua + self.TAna_, self.TDja_ + new_TDua + self.TDna_)

            if new_Tsv >= 0.0:
                # print(f"new_Tsv {new_Tsv} new_Vr {new_Vr}")
                self.Vr_ = new_Vr
                self.Tsv_ = new_Tsv
                self.TAua_ = new_TAua
                self.TDua_ = new_TDua
                self.Tsa_ = self.TAja_ + self.TAua_ + self.TAna_
                self.Tsd_ = self.TDja_ + self.TDua_ + self.TDna_

        self.Tsf_ = self.Tsa_ + self.Tsv_ + self.Tsd_

        print(
            f"self.TAja_ {self.TAja_} self.TAua {
                self.TAua_}  self.TAna_ {self.TAna_}"
        )
        print(
            f"self.TDja_ {self.TDja_} self.TDua {
                self.TDua_}  self.TDna_ {self.TDna_}"
        )

        print(
            f"Tsf {self.Tsf_} Tsa_ {self.Tsa_} Tsv_ {
                self.Tsv_}  Tsd_ {self.Tsd_}"
        )

    def plan_trapezoidal_original(self, Xf, Xi, Vi, Vf, Vmax, Amax, Dmax) -> bool:
        dX = Xf - Xi
        stop_dist = (Vi**2 - Vf**2) / (2.0 * Dmax)
        dXstop = np.copysign(stop_dist, Vi)
        s = sign_hard(dX - dXstop)
        self.Ar_ = s * Amax
        self.Dr_ = -s * Dmax
        self.Vr_ = s * Vmax

        if (s * Vi) > (s * self.Vr_):
            self.Ar_ = -s * Amax

        if (s * Vf) > (s * self.Vr_):
            self.Dr_ = s * Dmax

        self.Ta_ = (self.Vr_ - Vi) / self.Ar_
        self.Td_ = (Vf - self.Vr_) / self.Dr_

        dXmin = 0.5 * self.Ta_ * (self.Vr_ + Vi) + \
            0.5 * self.Td_ * (Vf + self.Vr_)

        if s * dX < s * dXmin:
            self.Vr_ = s * np.sqrt(
                max(
                    (self.Dr_ * Vi**2 - self.Ar_ * Vf **
                     2 + 2 * self.Ar_ * self.Dr_ * dX)
                    / (self.Dr_ - self.Ar_),
                    0.0,
                )
            )
            self.Ta_ = max(0.0, (self.Vr_ - Vi) / self.Ar_)
            self.Td_ = max(0.0, (Vf - self.Vr_) / self.Dr_)
            self.Tv_ = 0.0
        else:
            self.Tv_ = (dX - dXmin) / self.Vr_

        self.Tf_ = self.Ta_ + self.Tv_ + self.Td_
        self.Xi_ = Xi
        self.Xf_ = Xf
        self.Vi_ = Vi
        self.Vf_ = Vf
        self.Vmax_ = Vmax
        self.yAccel_ = Xi + Vi * self.Ta_ + 0.5 * self.Ar_ * self.Ta_**2

        print(
            f"self.Tf_ {self.Tf_}, self.Ta_ {self.Ta_} self.Tv_ {
                self.Tv_} self.Td_ {self.Td_}"
        )

        return True

    def plan_scurve(self, Xf, Xi, Vi, Vf, Vmax, Amax, Dmax) -> bool:

        # 为了加速/减速过程与梯形的时间一致，规划梯形时最大加/减速减版
        self.plan_trapezoidal_original(
            Xf, Xi, Vi, Vf, Vmax, Amax / 2, Dmax / 2)

        k = 2.0
        i = 2.0

        if self.Ta_ > 0.0:
            j = k / self.Ta_ * 2 * i
            (
                self.AJa_,
                self.AUa_,
                self.ANa_,
                self.TAja_,
                self.TAua_,
                self.TAna_,
            ) = self._velocityTrapezoidal(
                self.Vr_, self.Vi_, k * self.Ar_, j * self.Ar_, j * self.Ar_
            )
        else:
            (
                self.AJa_,
                self.AUa_,
                self.ANa_,
                self.TAja_,
                self.TAua_,
                self.TAna_,
            ) = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        if self.Td_ > 0.0:
            z = k / self.Td_ * 2 * i
            (
                self.DJa_,
                self.DUa_,
                self.DNa_,
                self.TDja_,
                self.TDua_,
                self.TDna_,
            ) = self._velocityTrapezoidal(
                self.Vf_,
                self.Vr_,
                k * self.Dr_ * -1,
                z * self.Dr_ * -1,
                z * self.Dr_ * -1,
            )
        else:
            (
                self.DJa_,
                self.DUa_,
                self.DNa_,
                self.TDja_,
                self.TDua_,
                self.TDna_,
            ) = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        # print(
        #     f"self.TAja_ {self.TAja_} self.TAua {self.TAua_}  self.TAna_ {self.TAna_}"
        # )
        # print(
        #     f"self.TDja_ {self.TDja_} self.TDua {self.TDua_}  self.TDna_ {self.TDna_}"
        # )

        print(f"self.AJa_ {self.AJa_} self.AUa_ {
              self.AUa_}  self.ANa_ {self.ANa_}")

        print(f"self.DJa_ {self.DJa_} self.DUa_ {
              self.DUa_}  self.DNa_ {self.DNa_}")

        self.Tsa_ = self.TAja_ + self.TAua_ + self.TAna_
        self.Tsd_ = self.TDja_ + self.TDua_ + self.TDna_

        # 匀速时间 = （总距离 - S加速距离 - S加速距离）/ 匀速度
        self.Tsv_ = self.calc_Tsv(self.Vr_, self.Tsa_, self.Tsd_)

        print(f"self.Vr_ {self.Vr_} Tsv_ {self.Tsv_} Vmax_ {self.Vmax_}")

        new_Vr = self.Vr_
        new_Tsv = self.Tsv_
        while new_Tsv > 0.0 and abs(new_Vr) < self.Vmax_:
            new_Vr *= 1.01
            if abs(new_Vr) >= self.Vmax_:
                new_Vr = sign_hard(self.Vr_) * self.Vmax_

            new_TAua = self.TAua_ + (new_Vr - self.Vr_) / self.AUa_
            new_TDua = self.TDua_ + (self.Vr_ - new_Vr) / self.DUa_

            new_Tsv = self.calc_Tsv(
                new_Vr, self.TAja_ + new_TAua + self.TAna_, self.TDja_ + new_TDua + self.TDna_)

            if new_Tsv >= 0.0:
                # print(f"new_Tsv {new_Tsv} new_Vr {new_Vr}")
                self.Vr_ = new_Vr
                self.Tsv_ = new_Tsv
                self.TAua_ = new_TAua
                self.TDua_ = new_TDua
                self.Tsa_ = self.TAja_ + self.TAua_ + self.TAna_
                self.Tsd_ = self.TDja_ + self.TDua_ + self.TDna_

        self.Tsf_ = self.Tsa_ + self.Tsv_ + self.Tsd_

        print(
            f"self.TAja_ {self.TAja_} self.TAua {
                self.TAua_}  self.TAna_ {self.TAna_}"
        )
        print(
            f"self.TDja_ {self.TDja_} self.TDua {
                self.TDua_}  self.TDna_ {self.TDna_}"
        )

        print(
            f"Tsf {self.Tsf_} Tsa_ {self.Tsa_} Tsv_ {
                self.Tsv_}  Tsd_ {self.Tsd_}"
        )

    # TODO: 在适当的计算步骤进行检查，若存在不符合要求的数值，则规划失败，返回False
    def plan_trapezoidal(self, Xf, Xi, Vi, Vf, Vmax, Amax, Dmax) -> bool:
        dX = Xf - Xi
        stop_dist = (Vi**2 - Vf**2) / (2.0 * Dmax)
        dXstop = np.copysign(stop_dist, Vi)
        s = sign_hard(dX - dXstop)
        self.Ar_ = s * Amax
        self.Dr_ = -s * Dmax
        self.Vr_ = s * Vmax

        if (s * Vi) > (s * self.Vr_):
            self.Ar_ = -s * Amax

        if (s * Vf) > (s * self.Vr_):
            self.Dr_ = s * Dmax

        self.Ta_ = (self.Vr_ - Vi) / self.Ar_
        self.Td_ = (Vf - self.Vr_) / self.Dr_

        dXmin = 0.5 * self.Ta_ * (self.Vr_ + Vi) + \
            0.5 * self.Td_ * (Vf + self.Vr_)

        if s * dX < s * dXmin:
            self.Vr_ = s * np.sqrt(
                max(
                    (self.Dr_ * Vi**2 - self.Ar_ * Vf **
                     2 + 2 * self.Ar_ * self.Dr_ * dX)
                    / (self.Dr_ - self.Ar_),
                    0.0,
                )
            )
            self.Ta_ = max(0.0, (self.Vr_ - Vi) / self.Ar_)
            self.Td_ = max(0.0, (Vf - self.Vr_) / self.Dr_)
            self.Tv_ = 0.0
        else:
            self.Tv_ = (dX - dXmin) / self.Vr_

        self.Tf_ = self.Ta_ + self.Tv_ + self.Td_
        self.Xi_ = Xi
        self.Xf_ = Xf
        self.Vi_ = Vi
        self.Vf_ = Vf
        self.Vmax_ = Vmax
        self.yAccel_ = Xi + Vi * self.Ta_ + 0.5 * self.Ar_ * self.Ta_**2

        print(
            f"self.Tf_ {self.Tf_}, self.Ta_ {self.Ta_} self.Tv_ {
                self.Tv_} self.Td_ {self.Td_}"
        )

        return True

    def eval(self, t):
        trajStep = self.Step()
        if t < 0.0:
            # Initial Condition
            trajStep.Y = self.Xi_
            trajStep.Yd = self.Vi_
            trajStep.Ydd = 0.0
        elif t <= self.Ta_:
            # Accelerating
            trajStep.Y = self.Xi_ + self.Vi_ * t + 0.5 * self.Ar_ * t**2
            trajStep.Yd = self.Vi_ + self.Ar_ * t
            trajStep.Ydd = self.Ar_
        elif t <= self.Ta_ + self.Tv_:
            # Coasting
            trajStep.Y = self.yAccel_ + self.Vr_ * (t - self.Ta_)
            trajStep.Yd = self.Vr_
            trajStep.Ydd = 0.0
        elif t <= self.Tf_:
            # Deceleration
            td = t - self.Tf_
            trajStep.Y = self.Xf_ + self.Vf_ * td + 0.5 * self.Dr_ * td**2
            trajStep.Yd = self.Vf_ + self.Dr_ * td
            trajStep.Ydd = self.Dr_
        else:
            # Final Condition
            trajStep.Y = self.Xf_
            trajStep.Yd = self.Vf_
            trajStep.Ydd = self.Dr_

        return trajStep

    def _velocityTrapezoidal(self, Vf, Vi, Amax, Aa, Da):
        # print(f"Amax {Amax} Aa {Aa}  Da {Da}")
        dV = Vf - Vi
        s = sign_hard(dV)
        Ja = s * Aa
        Na = -1 * s * Da
        Ua = s * Amax

        Tja = Ua / Ja  # 加速阶段时间
        Tna = -Ua / Na  # 减速阶段时间

        dVmin = 0.5 * Tja * Ua + 0.5 * Tna * Ua  # 最小速度变化量

        # print(f"s {s} dv {dV} dVmin {dVmin}")
        if s * dV < s * dVmin:
            # print("++++++++++++")
            Ua = s * np.sqrt(max((2 * Ja * Na * dV) / (Na - Ja), 0.0))
            Tja = max(0.0, Ua / Ja)
            Tna = max(0.0, -Ua / Na)
            Tua = 0.0  # 区间速度保持时间
        else:
            # print("------------")
            Tua = (dV - dVmin) / Ua

        # print(f"Ja {Ja} Na {Na}  Ua {Ua}")
        # print(f"Tja {Tja} Tua {Tua}  Tna {Tna}")

        return Ja, Ua, Na, Tja, Tua, Tna

    def eval_s(self, t):
        trajStep = self.Step()
        if t < 0.0:
            trajStep.Y = self.Xi_
            trajStep.Yd = self.Vi_
            trajStep.Ydd = 0.0

        elif t < self.Tsa_:

            # 加加速阶段
            if t < self.TAja_:
                trajStep.Y = self.Xi_ + self.Vi_*t + self.AJa_ * t ** 3 / 6.0
                trajStep.Yd = self.Vi_ + 0.5 * self.AJa_ * t**2
                trajStep.Ydd = self.AJa_ * t

            # 匀加速阶段
            elif t < self.TAja_ + self.TAua_:
                trajStep.Y = self.Xi_ + self.Vi_ * t + self.AUa_ / 6.0 * \
                    (3.0 * t ** 2 - 3.0 * self.TAja_ * t + self.TAja_ ** 2)
                trajStep.Yd = (
                    self.Vi_
                    + 0.5 * self.AJa_ * self.TAja_**2
                    + self.AUa_ * (t - self.TAja_)
                )
                trajStep.Ydd = self.AUa_

            # 减加速阶段
            else:
                t_tmp = t - self.Tsa_

                trajStep.Y = self.Xi_ + \
                    (self.Vr_ + self.Vi_) * self.Tsa_ / 2.0 + \
                    self.Vr_ * t_tmp + self.ANa_ * t_tmp ** 3 / 6.0
                trajStep.Yd = self.Vr_ + 0.5 * self.ANa_ * t_tmp**2
                trajStep.Ydd = self.ANa_ * t_tmp

        elif t < self.Tsa_ + self.Tsv_:

            trajStep.Y = self.Xi_ + (self.Vr_ + self.Vi_) * self.Tsa_ / \
                2.0 + self.Vr_ * (t - self.Tsa_)
            trajStep.Yd = self.Vr_
            trajStep.Ydd = 0.0

        elif t < self.Tsf_:
            # print(f"t {t}")
            td = t - self.Tsa_ - self.Tsv_
            t_tmp = t - self.Tsf_

            if td < self.TDja_:
                trajStep.Y = self.Xf_ - (self.Vr_ + self.Vf_) * self.Tsd_ / 2.0 + self.Vr_ * (
                    t_tmp + self.Tsd_) + self.DJa_ * (t_tmp + self.Tsd_) ** 3 / 6.0
                trajStep.Yd = self.Vr_ + 0.5 * self.DJa_ * td**2
                trajStep.Ydd = self.DJa_ * td

            elif td < self.TDja_ + self.TDua_:

                trajStep.Y = self.Xf_ - (self.Vr_ + self.Vf_) * self.Tsd_ / 2.0 + self.Vr_ * (t_tmp + self.Tsd_) + self.DUa_ / 6.0 * (
                    3.0 * (t_tmp + self.Tsd_) ** 2 - 3.0 * self.TDna_ * (t_tmp + self.Tsd_) + self.TDna_ ** 2)
                trajStep.Yd = (
                    self.Vr_
                    + 0.5 * self.DJa_ * self.TDja_**2
                    + self.DUa_ * (td - self.TDja_)
                )
                trajStep.Ydd = self.DUa_

            else:

                trajStep.Y = self.Xf_ + self.Vf_ * t_tmp + self.DNa_ * t_tmp ** 3 / 6.0
                trajStep.Yd = self.Vf_ + 0.5 * self.DNa_ * t_tmp**2
                trajStep.Ydd = self.DNa_ * t_tmp

        else:
            trajStep.Y = self.Xf_
            trajStep.Yd = self.Vf_
            trajStep.Ydd = 0

        return trajStep


def plot_sub(ax, time_steps, data, limits, title, xtitle="Time (s)", ytitle="Data") -> bool:
    data = np.array(data)
    upper_limit, lower_limit = max(limits), min(limits)

    # 画辅助线，上限和下限（细线，半透明）
    ax.plot(time_steps, [upper_limit] * len(time_steps), color='gray',
            linestyle='dashed', linewidth=1, alpha=0.8)
    ax.plot(time_steps, [lower_limit] * len(time_steps), color='gray',
            linestyle='dashed', linewidth=1, alpha=0.8)

    ax.plot(
        time_steps, data, label=title, linestyle="solid", color="green", linewidth=1.5, zorder=1
    )

    # 筛选数据点
    out_limits = np.where((data > upper_limit)
                          | (data < lower_limit))[0]
    within_limits = np.where((data <= upper_limit)
                             & (data >= lower_limit))[0]

    # 将超出上下限的数据点标为红色
    ax.scatter(time_steps[out_limits], data[out_limits],
               color='red', label='Out of Limit', s=2, zorder=2)

    # 将在上下限内的数据点标为绿色
    # ax.scatter(time_steps[within_limits], data[within_limits],
    #            color='green', label='Within Limits', s=2, zorder=2)

    ax.set_xlabel(xtitle)
    ax.set_ylabel(ytitle)
    ax.legend()
    ax.set_title(title, color='red' if out_limits.size else 'black')
    return out_limits.size == 0


def run_test_case_original(params: PlanParameters, traj: TrapezoidalTrajectory):
    result = []
    _Xf, _Xi, _Vi, _Vf, _Vmax, _Amax, _Dmax = params._Xf, params._Xi, params._Vi, params._Vf, params._Vmax, params._Amax, params._Dmax

    if abs(_Vi) > _Vmax or abs(_Vf) > _Vmax:
        print("Invalid test case, Initial and final velocity must be less than maximum velocity")
        return False

    # Plot the results
    plt.figure(figsize=(14, 8))

    # Add a centered title
    plt.suptitle(
        f"Xf={_Xf}, Xi={_Xi}, Vi={_Vi}, Vf={_Vf}, Vmax={
            _Vmax}, Amax={_Amax}, Dmax={_Dmax}",
        fontsize=16,
    )

    # Trapezoidal profile
    traj.plan_trapezoidal_original(
        Xf=_Xf, Xi=_Xi, Vi=_Vi, Vf=_Vf, Vmax=_Vmax, Amax=_Amax, Dmax=_Dmax
    )

    positions_t = []
    velocities_t = []
    accelerations_t = []

    step = TrapezoidalTrajectory.Step()
    time_steps_t = np.arange(0, traj.Tf_ + 0.01, 0.01)
    for t in time_steps_t:
        step = traj.eval(t)
        positions_t.append(step.Y)
        velocities_t.append(step.Yd)
        accelerations_t.append(step.Ydd)

    print(f"step.Y : {step.Y}")

    result.append(plot_sub(plt.subplot(3, 2, 1), time_steps_t, positions_t,
                           [traj.Xf_, traj.Xi_], "Trapezoidal Position", xtitle='', ytitle='Position (m)'))

    result.append(plot_sub(plt.subplot(3, 2, 3), time_steps_t, velocities_t,
                           [traj.Vf_, traj.Vi_, -_Vmax, _Vmax], "Trapezoidal Velocity", xtitle='', ytitle='Velocity (m/s)'))

    result.append(plot_sub(plt.subplot(3, 2, 5), time_steps_t, accelerations_t,
                           [traj.Dr_, traj.Ar_, _Amax, _Dmax], "Trapezoidal Acceleration", ytitle='Acceleration (m/ss)'))

    # S-curve profile
    traj.plan_scurve_original(Xf=_Xf, Xi=_Xi, Vi=_Vi, Vf=_Vf,
                              Vmax=_Vmax, Amax=_Amax, Dmax=_Dmax)

    positions_s = []
    velocities_s = []
    accelerations_s = []

    time_steps_s = np.arange(0, traj.Tsf_ + 0.01, 0.01)
    for t in time_steps_s:
        step = traj.eval_s(t)
        positions_s.append(step.Y)
        velocities_s.append(step.Yd)
        accelerations_s.append(step.Ydd)
    print(f"step.Y : {step.Y}")

    plot_sub(plt.subplot(3, 2, 2), time_steps_s, positions_s,
             [traj.Xf_, traj.Xi_], "S-Curve Position", xtitle='', ytitle='Position (m)')

    plot_sub(plt.subplot(3, 2, 4), time_steps_s, velocities_s,
             [traj.Vf_, traj.Vi_, _Vmax], "S-Curve Velocity", xtitle='', ytitle='Velocity (m/s)')

    plot_sub(plt.subplot(3, 2, 6), time_steps_s, accelerations_s,
             [traj.Dr_, traj.Ar_, _Amax, _Dmax], "S-Curve Acceleration", ytitle='Acceleration (m/ss)')

    # 调整子图之间的间距
    plt.subplots_adjust(hspace=0.4, wspace=0.2)

    # 添加鼠标悬停显示数值功能
    cursor = mplcursors.cursor(hover=True)
    cursor.connect(
        "add",
        lambda sel: sel.annotation.set_text(
            f"Time: {sel.target[0]:.2f}\nValue: {sel.target[1]:.3f}"
        ),
    )

    plt.show()
    return all(result)


def run_test_case(params: PlanParameters, traj: TrapezoidalTrajectory):
    _Xf, _Xi, _Vi, _Vf, _Vmax, _Amax, _Dmax = params._Xf, params._Xi, params._Vi, params._Vf, params._Vmax, params._Amax, params._Dmax
    # Trapezoidal profile
    return traj.plan_trapezoidal(
        Xf=_Xf, Xi=_Xi, Vi=_Vi, Vf=_Vf, Vmax=_Vmax, Amax=_Amax, Dmax=_Dmax
    )


# Example usage and plotting
if __name__ == "__main__":
    traj = TrapezoidalTrajectory()
    params_true = PlanParameters(
        Xi=0.0, Xf=10.0, Vi=0.0, Vf=2.0, Vmax=2.0, Amax=0.5, Dmax=0.5
    )

    params_false = PlanParameters(
        Xi=0.0, Xf=1.0, Vi=0.0, Vf=2.0, Vmax=2.0, Amax=0.5, Dmax=0.5
    )

    # 首先测试下“无效规划判断标准”是否正确
    assert run_test_case_original(
        params_true, traj) == True, "Test case failed"

    assert run_test_case_original(
        params_false, traj) == False, "Test case failed"

    # 测试优化后的算法是否与“无效规划判断标准”的判断结果一致
    test_cases: list[PlanParameters] = []
    test_cases.append(params_true)
    test_cases.append(params_false)
    # TODO: 添加一些测试用例，以PlanParameters类型作为测试用例的输入

    for params in test_cases:
        try:
            result = run_test_case(params, traj)
            result_original = run_test_case_original(params, traj)
            assert result == result_original
        except Exception as err:
            print(f"\033[1;31mTest case failed: {params}\033[0m")
            print(f"\033[1;31mShould have {
                  result_original}, but got {result}\033[0m")
