from core.advbase import *


class Akasha(Adv):
    def prerun(self):
        self.team_sp = 0

    def s2_charge_sp(self, t):
        self.charge(t.name, 420)
        self.team_sp += 420

    def s2_proc(self, e):
        charge_timer = Timer(self.s2_charge_sp, 1.5, True)
        charge_timer.name = e.name
        EffectBuff(
            "sp_regen_zone", 10, lambda: charge_timer.on(), lambda: charge_timer.off()
        ).no_bufftime().on()

    def post_run(self, end):
        # self.stats.append(f'team_sp:{self.team_sp}')
        self.comment = f"total {self.team_sp} SP to team from s2"


variants = {None: Akasha}
