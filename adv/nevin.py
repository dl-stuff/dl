from core.slots import SlotBase
from core.advbase import *
from module.template import SigilAdv


class Nevin(SigilAdv):
    def prerun(self):
        # alt s1 doesn't add dps
        self.config_sigil(duration=300, x=True, s2=True)

        t = Timer(self.x_sword_dmg, 1.5, True)
        self.sword = EffectBuff("revelation_sword", 12, lambda: t.on(), lambda: t.off()).no_bufftime()
        self.sigil_listeners = [Listener("dragon", self.a_shift_sigil)]

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.zone = ZoneTeambuff()

    def x_sword_dmg(self, e):
        for _ in range(4):
            self.dmg_make("#revelation_sword", 1.00, "#")
            self.add_combo()

    def x_sigil_proc(self, e):
        if e.index == 6:
            self.sword.on()

    def s2_proc(self, e):
        if not isinstance(self, Nevin) or self.unlocked:
            for aseq in range(self.zonecount):
                self.hitattr_make(e.name, e.base, e.group, aseq + 1, self.conf[e.name].extra_self, dtype=e.dtype)
        else:
            self.a_update_sigil(-60)

    def a_shift_sigil(self, t):
        self.a_update_sigil(-240)


class Nevin_UNLOCKED(Nevin):
    SAVE_VARIANT = False

    def prerun(self):
        super().prerun()
        self.a_update_sigil(-300)


variants = {None: Nevin, "UNLOCKED": Nevin_UNLOCKED}
