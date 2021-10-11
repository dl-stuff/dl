from core.advbase import *
from core.acl import CONTINUE
from module.template import SigilAdv


class Ryszarda(SigilAdv):
    def prerun(self):
        self.config_sigil(duration=300, x=True)
        self.sigil_listeners = [Listener("heal", self.a1_healed)]
        self.x5_level = 0

    def a1_healed(self, e):
        if not self.is_set_cd("a1", 20):
            self.a_update_sigil(-30)
            if e.delta >= 1000:
                self.a_update_sigil(-15)

    @allow_acl
    def x5_sigil_lvl(self, lvl):
        self.x5_level = int(lvl)
        return CONTINUE

    def _next_x(self):
        prev = self.action.getprev()
        if self.x5_level and self.unlocked and isinstance(prev, X) and prev.index == 4:
            return self.a_x_dict[f"sigil{self.x5_level}"][5]()
        return super()._next_x()


class Ryszarda_UNLOCKED(Ryszarda):
    SAVE_VARIANT = False

    def prerun(self):
        super().prerun()
        self.a_update_sigil(-300)


variants = {None: Ryszarda, "UNLOCKED": Ryszarda_UNLOCKED}
