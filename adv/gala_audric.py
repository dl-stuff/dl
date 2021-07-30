from core.advbase import *
from module.template import SkillChainAdv


class Gala_Audric(SkillChainAdv):
    def prerun(self):
        super().prerun()
        self.a1_count = 5
        self.a1_mod = Modifier("a1_spd", "spd", "passive", 0.0)
        Event("s").listener(self.a1_check, order=2)
        Event("ds").listener(self.a1_check, order=2)

    def a1_check(self, e):
        if self.a1_count > 0:
            self.a1_count -= 1
            self.a1_mod.mod_value += 0.02
        if not self.is_set_cd("a1_amp", 30):
            self.add_amp(amp_id="20000", max_level=3)


variants = {None: Gala_Audric}
