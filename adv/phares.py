from core.advbase import *


class Phares(Adv):
    def prerun(self):
        super().prerun()
        self.l_aff_amp = [Listener(affname, self.a1_amp) for affname in AFFLICT_LIST]

    def a1_amp(self, e):
        # poison, burn, paralysis, frostbite, stormlash, flashburn, shadowblight, scorchrend
        if not self.is_set_cd("a1_amp", 8):
            self.add_amp(max_level=1)

    def s2_before(self, e):
        if e.group == "ddrive" and not self.is_set_cd("s2_extend_aff", 15, hidden=True):
            for aff_name in ("poison", "burn", "paralysis", "frostbite", "stormlash", "flashburn", "shadowblight", "scorchrend"):
                aff = getattr(self.afflics, aff_name)
                for timer in aff.active_t:
                    timer.add(min(timer.max_duration - timer.elapsed(), 15))


variants = {None: Phares}
