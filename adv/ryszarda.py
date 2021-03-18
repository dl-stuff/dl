from core.advbase import *
from core.acl import CONTINUE
from module.template import SigilAdv


class Ryszarda(SigilAdv):
    def prerun(self):
        self.config_sigil(duration=300, x=True)
        self.heal_event.listener(self.a1_healed)
        self.a1_heal_cd = False
        self.x5_level = 0

    def a1_heal_cd_off(self, t):
        self.a1_heal_cd = False

    def a1_healed(self, e):
        if not self.a1_heal_cd:
            self.a_update_sigil(-30)
            # bullshit maffs
            if e.delta >= 1000:
                self.a_update_sigil(-15)
            self.a1_heal_cd = True
            Timer(self.a1_heal_cd_off).on(20)

    @allow_acl
    def x5_sigil_lvl(self, lvl):
        self.x5_level = int(lvl)
        return CONTINUE

    def x(self):
        prev = self.action.getprev()
        if self.x5_level and self.unlocked and isinstance(prev, X) and prev.index == 4:
            return self.a_x_dict[f"sigil{self.x5_level}"][5]()
        return super().x()


class Ryszarda_UNLOCKED(Ryszarda):
    def prerun(self):
        super().prerun()
        self.a_update_sigil(-300)


variants = {None: Ryszarda, "UNLOCKED": Ryszarda_UNLOCKED}
