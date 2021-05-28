from core.advbase import *
from core.acl import CONTINUE

a3_stack_cap = 10


# Using Mascula's initial skill, displayed at the
# top of his skill list, grants him a strength amp
# with a maximum team amp level of three.
# After this amp is granted, this ability will not
# grant it again for 20 seconds.

# Master Control (granted by his second skill)
# grants Mascula the following effects:

# ・His standard attacks are buffed and deal
# additional blows to multiple nearby targets.
# ・The fourth attack in his standard attack
# combo dispels one enemy buff.
# ・His attack rate is increased by 6%.
# ・When the combo count is 30 or higher,
# his strength is increased by 10%,
# his critical rate by 8%, and 8% is added
# to the modifier applied to his critical damage.

# When Master Control is lost, the skill gauge
# for Mascula's second skill will be filled by 50%.
# Also, Master Control will be lost upon
# shapeshifting.
class Gala_Mascula(Adv):
    def prerun(self):
        self.slots.c.set_need_bufftime()
        self.amplified_current = 0
        self.amplified_current_buff = EffectBuff("amplified_current", 11, self.amplified_current_on, self.amplified_current_off, source="s1")

        self.masterctrl_buff = EffectBuff("masterctrl", 26, self.masterctrl_on, self.masterctrl_off)
        self.masterctrl_mods = [
            Modifier("masterctrl_att", "att", "passive", 0.1, get=self.masterctrl_30c),
            Modifier("masterctrl_cc", "crit", "chance", 0.08, get=self.masterctrl_30c),
            Modifier("masterctrl_cd", "crit", "damage", 0.08, get=self.masterctrl_30c),
            Modifier("masterctrl_spd", "spd", "passive", 0.06, get=self.masterctrl_buff.get),
        ]
        self.masterctrl = ModeManager(
            name="masterctrl",
            group="masterctrl",
            duration=26,
            buffs=[self.masterctrl_buff],
            x=True,
            s1=True,
            s2=True,
            fs=True,
            source="s2",
        )
        self.masterctrl_buff.hidden = False
        Event("dragon").listener(lambda _: self.masterctrl.off())

        self.a3_crit_buffs = []
        self.a3_crit_chance = 0
        self.a3_crit_dmg_stack = 0
        self.a3_crit_dmg_buff = Selfbuff("a3_crit_dmg", 0.00, -1, "crit", "damage")

        self.crit_mod = self.ev_custom_crit_mod
        self.rngcrit_states = {(None, 0): 1.0}
        self.rngcrit_cd_duration = 1
        self.prev_log_time = 0

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.current_s[dst] = "masterctrl"

    def amplified_current_on(self):
        self.amplified_current = 1

    def amplified_current_off(self):
        self.amplified_current = 0

    def masterctrl_30c(self):
        return self.hits >= 30 and self.masterctrl_buff.get()

    def masterctrl_on(self):
        pass

    def masterctrl_off(self):
        self.current_s["s2"] = "default"
        self.charge_p("masterctrl", 0.5, target="s2")

    def s1_proc(self, e):
        if e.group == "masterctrl":
            self.amplified_current_buff.on()

    def s2_proc(self, e):
        if e.group != "masterctrl":
            self.masterctrl.on()

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


variants = {None: Gala_Mascula}
