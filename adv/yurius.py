from core.advbase import *


class Yurius_DDRIVE(Adv):
    SAVE_VARIANT = False
    comment = "infinite ddrive gauge"

    def prerun(self):
        self.dragonform.set_utp_infinite()


variants = {None: Adv, "DDRIVE": Yurius_DDRIVE}
