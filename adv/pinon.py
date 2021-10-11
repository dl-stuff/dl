from core.advbase import *
from module.template import SigilAdv


class Pinon(SigilAdv):
    def fs2_proc(self, e):
        if not self.unlocked:
            self.a_update_sigil(-13)

    def prerun(self):
        self.config_sigil(duration=300, x=True)


class Pinon_UNLOCKED(Pinon):
    SAVE_VARIANT = False

    def prerun(self):
        super().prerun()
        self.a_update_sigil(-300)


variants = {None: Pinon, "UNLOCKED": Pinon_UNLOCKED}
