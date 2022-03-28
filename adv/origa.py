from core.advbase import *
from module.template import SigilAdv


class Origa(SigilAdv):
    S2_SP_MOD = 0.35

    def prerun(self):
        self.dragonform.set_disabled("origa_a1")
        self.config_sigil(duration=300)

    def _add_sp_fn(self, s, name, sp):
        if s.name == "s2" and not self.dragonform.in_ddrive():
            sp = float_ceil(sp, self.sp_mod(name, target=s.name) * self.S2_SP_MOD)
        else:
            sp = float_ceil(sp, self.sp_mod(name, target=s.name))
        s.charge(sp)
        return sp

    def _prep_sp_fn(self, s, _, percent):
        if s.name == "s2" and not self.dragonform.in_ddrive():
            sp = float_ceil(s.real_sp, percent * self.S2_SP_MOD)
        else:
            sp = float_ceil(s.real_sp, percent)
        s.charge(sp)
        return sp

    @allow_acl
    def dodge(self):
        if self.dragonform.in_ddrive() and isinstance(self.action.getdoing(), X):
            return self.a_dodge_on_x()
        return self.a_dodge()

    def s2_proc(self, e):
        if not self.unlocked:
            self.a_update_sigil(-300)
            self.dragonform.unset_disabled("origa_a1")


variants = {None: Origa}
