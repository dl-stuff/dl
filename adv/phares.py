from core.advbase import *


class Phares(Adv):
    def prerun(self):
        super().prerun()
        self.l_aff_amp = [Listener(affname, self.a1_amp) for affname in AFFLICT_LIST]

    def a1_amp(self, e):
        # poison, burn, paralysis, frostbite, stormlash, flashburn, shadowblight, scorchrend
        if not self.is_set_cd("a1_amp", 8):
            self.add_amp(max_level=2)

    def s2_before(self, e):
        if e.group == "ddrive":
            for aff_name in ("poison", "burn", "paralysis", "frostbite", "stormlash", "flashburn", "shadowblight", "scorchrend"):
                aff = getattr(self.afflics, aff_name)
                for timer in aff.active_t:
                    # yabai
                    if not self.is_set_cd(f"s2_{aff_name}_{id(timer)}", 15, hidden=True):
                        timer.add(min(timer.max_duration, 15))


variants = {None: Phares}
