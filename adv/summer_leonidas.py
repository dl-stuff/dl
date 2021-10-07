from core.advbase import *


class Summer_Leonidas_DDRIVE(Adv):
    SAVE_VARIANT = False
    comment = "infinite ddrive gauge"

    def prerun(self):
        self.dragonform.set_utp_infinite()


variants = {None: Adv, "DDRIVE": Summer_Leonidas_DDRIVE}
