from core.advbase import *


class Yukimura(Adv):
    comment = "always use full taps for s1 s2"

    def s1_proc(self, e):
        if e.group == 2:
            self.a_s_dict["s1"].enable_phase_up = False
            self.current_s["s1"] = "monke"
            self.current_s["s2"] = "monke"
            self.current_x = "monke"
            self.current_fs = "monke"
            self.a_dodge = Dodge("dodge", self.conf.dodge_monke)
            self.a_dash = DashX("dash", self.conf.dash_monke)
            Modifier("monke_sd", "s", "passive", 0.4).on()
            Modifier("monke_att", "att", "passive", 0.1).on()
            self.monkey_burst = BurstGambit("monkey_burst", 15, self.monkey_burst_on, self.monkey_burst_off)
        elif e.group == "monke":
            self.monkey_burst.on()
            self.monkey_burst.on()

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.current_s[dst] = "monke"

    def monkey_burst_on(self):
        self.monkey_burst_dmg = self.dmg_formula("s", 43.0)

    def monkey_burst_off(self):
        self.dmg_make("s1_monke_monkey_burst", self.monkey_burst_dmg, fixed=True)
        self.monkey_burst_dmg = 0

    @allow_acl
    def dash(self):
        log("dash", str(self.a_dash))
        if self.in_dform() or not self.a_dash:
            return False
        return self.a_dash()

    @property
    def monke(self):
        return self.current_s["s1"] == "monke"


variants = {None: Yukimura}
