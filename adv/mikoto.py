from core.advbase import *
from module.template import RngCritAdv


class Mikoto(RngCritAdv):
    def prerun(self):
        self.config_rngcrit(cd=15, ev=20)
        self.a1_stack = 0

    def charge(self, name, sp, target=None):
        sp_s1 = self.sp_convert(self.sp_mod(name) + 0.1 * self.a1_stack, sp)
        sp = self.sp_convert(self.sp_mod(name), sp)
        targets = self.get_targets(target)
        if not targets:
            return
        for s in targets:
            if s == self.s1:
                s.charge(sp_s1)
            else:
                s.charge(sp)
        self.think_pin("sp")
        log(
            "sp",
            name if not target else f"{name}_{target}",
            sp,
            ", ".join([f"{s.charged}/{s.sp}" for s in self.skills]),
        )

    def rngcrit_cb(self, mrate=None):
        self.a1_stack = mrate

    @property
    def buffcount(self):
        buffcount = super().buffcount
        return buffcount + self.a1_stack


variants = {None: Mikoto}
