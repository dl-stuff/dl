from core.advbase import *
from core.acl import CONTINUE

a3_stack_cap = 10


class Gala_Laxi(Adv):
    RESONANT_DEF = 0.20
    RESONANT_SD = 0.15
    RESONANT_STR = 0.15
    FIG_DAMAGE = 0.333

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # human latency penalty on ex combo
        # for xn, xnconf in self.conf.find(r'^x\d+_ex$'):
        #     xnconf['startup'] += 0.05

    def prerun(self):
        self.x_fig_t = Timer(self.x_fig_dmg, 0.33, True).off()
        self.fig = EffectBuff("fig", 20, self.x_fig_on, self.x_fig_off)

        self.a1_cp = 0
        self.a1_buffs = {
            33: Selfbuff("a1_defense", self.RESONANT_DEF, -1, "defense", "buff"),
            66: Selfbuff("a1_sd", self.RESONANT_SD, -1, "s", "buff"),
            100: Selfbuff("a1_str", self.RESONANT_STR, -1, "att", "buff"),
        }
        self.a3_crit_buffs = []
        self.a3_crit_chance = 0
        self.a3_crit_dmg_stack = 0
        self.a3_crit_dmg_buff = Selfbuff("a3_crit_dmg", 0.00, -1, "crit", "damage")

        self.current_x = "default"
        self.deferred_x = "ex"
        Event("s").listener(self.reset_to_norm, order=0)

        self.crit_mod = self.ev_custom_crit_mod
        self.rngcrit_states = {(None, 0): 1.0}
        self.rngcrit_cd_duration = 1
        self.prev_log_time = 0

    @property
    def buffcount(self):
        buffcount = super().buffcount
        return buffcount + self.a3_crit_dmg_stack

    def rngcrit_cb(self, mrate=None):
        self.a3_crit_dmg_stack = mrate - 1
        new_value = 0.04 * mrate
        if not self.a3_crit_dmg_buff.get():
            self.a3_crit_dmg_buff.set(new_value)
            self.a3_crit_dmg_buff.on()
        else:
            self.a3_crit_dmg_buff.value(new_value)

    def ev_custom_crit_mod(self, name):
        # print(f'{now():.02f}', self.a3_crit_dmg_stack+1, flush=True)
        if name == "test" or self.a3_crit_dmg_stack >= 9:
            return self.solid_crit_mod(name)
        else:
            chance, cdmg = self.combine_crit_mods()
            t = now()

            new_states = defaultdict(lambda: 0.0)
            for state, state_p in self.rngcrit_states.items():
                if state[1] == a3_stack_cap:
                    new_states[(-1, a3_stack_cap)] += state_p
                elif state[0] is not None and t - state[0] < self.rngcrit_cd_duration:
                    new_states[state] += state_p
                else:
                    miss_rate = 1.0 - chance
                    new_states[state] += miss_rate * state_p
                    new_stack = state[1] + 1
                    new_states[(t, new_stack)] += chance * state_p

            new_states[(None, 0)] += 1 - sum(new_states.values())

            mrate = reduce(lambda mv, s: mv + (s[0][1] * s[1]), new_states.items(), 0)
            if self.prev_log_time == 0 or self.prev_log_time < t - self.rngcrit_cd_duration:
                log("rngcrit", mrate)
                self.prev_log_time = t
            self.rngcrit_cb(mrate)
            self.rngcrit_states = new_states

            return chance * (cdmg - 1) + 1

    @allow_acl
    def norm(self):
        if self.current_x != "default" and isinstance(self.action.getdoing(), X):
            self.deferred_x = "default"
        return CONTINUE

    @allow_acl
    def ex(self):
        if self.current_x != "ex" and isinstance(self.action.getdoing(), X):
            self.deferred_x = "ex"
        return CONTINUE

    def reset_to_norm(self, e):
        self.current_x = "default"

    def x(self, x_min=1):
        prev = self.action.getprev()
        if isinstance(prev, X) and (prev.group == self.current_x or "ex" in (prev.group, self.current_x)):
            if self.deferred_x is not None:
                log("deferred_x", self.deferred_x)
                self.current_x = self.deferred_x
                self.deferred_x = None
            if prev.index < self.conf[prev.group].x_max:
                x_next = self.a_x_dict[self.current_x][prev.index + 1]
            else:
                x_next = self.a_x_dict[self.current_x][x_min]
            if x_next.enabled:
                return x_next()
            else:
                self.current_x = "default"
        return self.a_x_dict[self.current_x][x_min]()

    def x_fig_on(self):
        self.x_fig_t.on()
        self.current_s["s1"] = "eden"
        self.current_s["s2"] = "eden"

    def x_fig_off(self):
        self.x_fig_t.off()
        self.current_s["s1"] = "default"
        self.current_s["s2"] = "default"
        self.a1_update(-100)

    def x_fig_dmg(self, t):
        if any([s_dict.ac.status != -2 for s_dict in self.a_s_dict.values()]):
            return
        if self.dragonform.status != -2:
            return
        self.dmg_make("#fig", self.FIG_DAMAGE)
        self.add_combo("#fig")

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None):
        self.a1_update(attr.get("cp", 0))
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit)

    def a1_update(self, delta):
        if delta != 0 and not self.fig.get() and self.a1_cp < 100:
            next_cp = max(min(self.a1_cp + delta, 100), 0)
            delta = next_cp - self.a1_cp
            if delta == 0:
                return
            if not self.nihilism:
                if delta > 0:
                    for thresh, buff in self.a1_buffs.items():
                        if self.a1_cp < thresh and next_cp >= thresh:
                            buff.on()
                else:
                    for thresh, buff in self.a1_buffs.items():
                        if next_cp < thresh:
                            buff.off()
            self.a1_cp = next_cp
            log("galaxi", "cp", self.a1_cp)

    def add_combo(self, name="#"):
        result = super().add_combo(name)
        if self.nihilism:
            return result
        if not result:
            for c in self.a3_crit_buffs:
                c.off()
            self.a3_crit_buffs = []
            self.rngcrit_states = {(None, 0): 1.0}
            self.prev_log_time = 0
        a_hits = self.hits // 15
        if len(self.a3_crit_buffs) < 3 and self.condition("always connect hits") and a_hits > len(self.a3_crit_buffs):
            self.a3_crit_buffs.append(Selfbuff("a3_crit_chance", 0.04, -1, "crit", "chance").on())
        return result

    def s2_proc(self, e):
        if e.group == "default":
            self.fig.on()


class Gala_Laxi_70MC(Gala_Laxi):
    RESONANT_DEF = 0.25
    RESONANT_SD = 0.20
    RESONANT_STR = 0.20
    comment = "70 MC"
    conf = {
        "c": {
            "name": "Gala Laxi",
            "icon": "100032_04_r05",
            "att": 599,
            "hp": 908,
            "ele": "flame",
            "wt": "dagger",
            "spiral": True,
            "a": [["resself_stun_att", 0.15, 10.0, 15.0], ["resself_sleep_att", 0.15, 10.0, 15.0], ["affres_stun", 100.0], ["affres_sleep", 100.0]],
        },
        "fs": {
            "charge": 0.15,
            "startup": 0.26667,
            "recovery": 0.5,
            "attr": [
                {"dmg": 0.258, "sp": 288, "cp": 1},
                {"dmg": 0.258, "cp": 1, "msl": 0.05},
                {"dmg": 0.258, "cp": 1, "msl": 0.1},
                {"dmg": 0.258, "cp": 1, "msl": 0.15},
                {"dmg": 0.258, "cp": 1, "msl": 0.2},
                {"dmg": 0.258, "cp": 1, "msl": 0.25},
            ],
            "interrupt": {"s": 0.0, "dodge": 0.0},
            "cancel": {"s": 0.0, "dodge": 0.0},
        },
        "s1": {
            "sp": 2476,
            "startup": 0.1,
            "recovery": 1.26667,
            "attr": [{"dmg": 2.13, "afflic": ["burn", 120, 0.97], "iv": 0.13333}, {"dmg": 2.13, "iv": 0.33333}, {"dmg": 2.13, "iv": 0.53333}, {"dmg": 2.13, "iv": 0.93333}],
        },
        "s1_eden": {
            "sp": 2476,
            "startup": 0.1,
            "recovery": 2.0,
            "attr": [
                {"dmg": 0.76, "afflic": ["scorchrend", 120, 0.416], "iv": 0.13333},
                {"dmg": 1.26, "iv": 0.2},
                {"dmg": 0.76, "iv": 0.33333},
                {"dmg": 1.26, "iv": 0.4},
                {"dmg": 1.0, "iv": 0.53333},
                {"dmg": 1.26, "iv": 0.6},
                {"dmg": 1.0, "iv": 0.93333},
                {"dmg": 1.26, "iv": 1.0},
                {"dmg": 1.26, "iv": 1.16667},
                {"dmg": 1.0, "iv": 1.33333},
                {"dmg": 1.26, "iv": 1.66667},
                {"dmg": 1.0, "iv": 1.66667},
            ],
        },
        "s2": {"sp": 7732, "startup": 0.1, "recovery": 1.33333},
        "s2_eden": {"sp": 3736, "startup": 0.1, "recovery": 1.16667, "attr": [{"dmg": 5.7, "iv": 0.33333}, {"dmg": 5.7, "iv": 0.5}, {"dmg": 5.7, "iv": 0.7}, {"dmg": 6.26, "iv": 0.86667}]},
        "x1": {
            "startup": 0.2,
            "recovery": 0.3,
            "attr": [{"sp": 172}, {"dmg": 0.62, "cp": 1, "msl": 0.2}, {"dmg": 0.62, "cp": 1, "msl": 0.4}],
            "interrupt": {"s": 0.0, "fs": 0.0, "dodge": 0.0},
            "cancel": {"s": 0.0, "fs": 0.0, "dodge": 0.0},
        },
        "x1_ex": {
            "startup": 0.2,
            "recovery": 0.3,
            "attr": [{"sp": 216}, {"dmg": 0.34, "cp": 1, "msl": 0.1}, {"dmg": 0.34, "cp": 1, "msl": 0.2}, {"dmg": 0.34, "cp": 1, "msl": 0.3}, {"dmg": 0.34, "cp": 1, "msl": 0.4}],
            "interrupt": {"s": 0.0, "fs": 0.0, "dodge": 0.0},
            "cancel": {"s": 0.0, "fs": 0.0, "dodge": 0.0},
        },
        "x2": {
            "startup": 0.16667,
            "recovery": 0.33333,
            "attr": [{"sp": 172}, {"dmg": 0.68, "cp": 1, "msl": 0.2}, {"dmg": 0.68, "cp": 1, "msl": 0.4}],
            "interrupt": {"s": 0.0, "fs": 0.0, "dodge": 0.0},
            "cancel": {"s": 0.0, "fs": 0.0, "dodge": 0.0},
        },
        "x2_ex": {
            "startup": 0.16667,
            "recovery": 0.33333,
            "attr": [{"sp": 216}, {"dmg": 0.37, "cp": 1, "msl": 0.1}, {"dmg": 0.37, "cp": 1, "msl": 0.2}, {"dmg": 0.37, "cp": 1, "msl": 0.3}, {"dmg": 0.37, "cp": 1, "msl": 0.4}],
            "interrupt": {"s": 0.0, "fs": 0.0, "dodge": 0.0},
            "cancel": {"s": 0.0, "fs": 0.0, "dodge": 0.0},
        },
        "x3": {
            "startup": 0.16667,
            "recovery": 0.33333,
            "attr": [{"sp": 315}, {"dmg": 0.74, "cp": 1, "msl": 0.2}, {"dmg": 0.74, "cp": 1, "msl": 0.4}],
            "interrupt": {"s": 0.0, "fs": 0.0, "dodge": 0.0},
            "cancel": {"s": 0.0, "fs": 0.0, "dodge": 0.0},
        },
        "x3_ex": {
            "startup": 0.16667,
            "recovery": 0.33333,
            "attr": [{"sp": 396}, {"dmg": 0.4, "cp": 1, "msl": 0.1}, {"dmg": 0.4, "cp": 1, "msl": 0.2}, {"dmg": 0.4, "cp": 1, "msl": 0.3}, {"dmg": 0.4, "cp": 1, "msl": 0.4}],
            "interrupt": {"s": 0.0, "fs": 0.0, "dodge": 0.0},
            "cancel": {"s": 0.0, "fs": 0.0, "dodge": 0.0},
        },
        "x4": {
            "startup": 0.4,
            "recovery": 0.26667,
            "attr": [{"dmg": 0.77, "sp": 344, "cp": 2}, {"dmg": 0.77, "cp": 2, "iv": 0.1}, {"dmg": 0.8, "cp": 2, "iv": 0.2}],
            "interrupt": {"s": 0.0},
            "cancel": {"s": 0.0, "fs": 0.4, "dodge": 0.4},
        },
        "x4_ex": {
            "startup": 0.26667,
            "recovery": 0.23333,
            "attr": [
                {"dmg": 0.44, "sp": 432, "cp": 2},
                {"dmg": 0.44, "cp": 2, "msl": 0.05},
                {"dmg": 0.44, "cp": 2, "msl": 0.1},
                {"dmg": 0.44, "cp": 2, "msl": 0.15},
                {"dmg": 0.44, "cp": 2, "msl": 0.2},
                {"dmg": 0.44, "cp": 2, "msl": 0.25},
            ],
            "interrupt": {"s": 0.0, "fs": 0.0, "dodge": 0.0},
            "cancel": {"s": 0.0, "fs": 0.0, "dodge": 0.0},
        },
    }

    def prerun(self):
        super().prerun()
        self.ahits = 0

    def add_combo(self, name="#"):
        result = super().add_combo(name)
        if self.condition("always connect hits"):
            a_hits = self.hits // 15
            if a_hits > 0 and a_hits != self.ahits and not self.is_set_cd("a3", 30):
                self.ahits = a_hits
                self.add_one_att_amp()
        return result


variants = {None: Gala_Laxi, "70MC": Gala_Laxi_70MC}
