from core.advbase import *


class Housekeeper_Pia(Adv):
    comment = "no counter on s2"

    def prerun(self):
        self.heal_event.listener(self.l_heal_amp)

    def l_heal_amp(self, _):
        if not self.is_set_cd("a3", 20):
            self.add_amp(amp_id="20000")


class Housekeeper_Pia_COUNTER(Housekeeper_Pia):
    comment = "always counter on s2"

    def prerun(self):
        super().prerun()
        self.conf.s2.attr = self.conf.s2.attr_counter


variants = {None: Housekeeper_Pia, "COUNTER": Housekeeper_Pia_COUNTER}
