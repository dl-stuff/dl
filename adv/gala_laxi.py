from core.advbase import *
from core.acl import CONTINUE
from module.template import LowerMCAdv
from conf import DEFAULT

a3_stack_cap = 10


class Gala_Laxi(Adv):
    RESONANT_DEF = 0.25
    RESONANT_SD = 0.20
    RESONANT_STR = 0.20
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

        self.current_x = DEFAULT
        self.deferred_x = "ex"

        self.crit_mod = self.ev_custom_crit_mod
        self.rngcrit_states = {(None, 0): 1.0}
        self.rngcrit_cd_duration = 1
        self.prev_log_time = 0

        self.a3_hits = None

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
        if self.current_x != DEFAULT and isinstance(self.action.getdoing(), X):
            self.deferred_x = DEFAULT
        return CONTINUE

    @allow_acl
    def ex(self):
        if self.current_x != "ex" and isinstance(self.action.getdoing(), X):
            self.deferred_x = "ex"
        return CONTINUE

    def _next_x(self):
        if self.current_x == "ex" and not isinstance(self.action.getdoing(), X):
            self.current_x = DEFAULT
        return super()._next_x()

    def x_fig_on(self):
        self.x_fig_t.on()
        self.current_s["s1"] = "eden"
        self.current_s["s2"] = "eden"

    def x_fig_off(self):
        self.x_fig_t.off()
        self.current_s["s1"] = DEFAULT
        self.current_s["s2"] = DEFAULT
        self.a1_update(-100)

    def x_fig_dmg(self, t):
        if self.in_dform() or isinstance(self.action.getdoing(), S):
            return
        self.dmg_make("#fig", self.FIG_DAMAGE)
        self.add_combo("#fig")

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None, dtype=None):
        self.a1_update(attr.get("cp", 0))
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit, dtype=dtype)

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
        if self.condition("always connect hits"):
            if len(self.a3_crit_buffs) < 3 and a_hits > len(self.a3_crit_buffs):
                self.a3_crit_buffs.append(Selfbuff("a3_crit_chance", 0.04, -1, "crit", "chance").on())
            if self.MC is None:
                if a_hits > 0 and a_hits != self.a3_hits and not self.is_set_cd("a3", 30):
                    self.a3_hits = a_hits
                    self.add_amp(max_level=3)
        return result

    def s2_proc(self, e):
        if e.group == DEFAULT:
            self.fig.on()


class Gala_Laxi_50MC(Gala_Laxi, LowerMCAdv):
    RESONANT_DEF = 0.20
    RESONANT_SD = 0.15
    RESONANT_STR = 0.15


variants = {None: Gala_Laxi, "50MC": Gala_Laxi_50MC}
