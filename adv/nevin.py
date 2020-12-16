from core.advbase import *
from module.template import SigilAdv

class Nevin(SigilAdv):
    def prerun(self):
        # alt s1 doesn't add dps
        self.config_sigil(duration=300, x=True, s2=True)

        t = Timer(self.x_sword_dmg, 1.5, True)
        self.sword = EffectBuff('revelation_sword', 12, lambda: t.on(), lambda: t.off()).no_bufftime()
        Event('dragon').listener(self.a_shift_sigil)

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.unlocked = True
        adv.zone = ZoneTeambuff()

    def x_sword_dmg(self, e):
        for _ in range(4):
            self.dmg_make('#revelation_sword', 1.00, '#')
            self.add_combo()

    def x_sigil_proc(self, e):
        if e.index == 6:
            self.sword.on()

    def s2_proc(self, e):
        if self.unlocked:
            for aseq in range(self.zonecount):
                self.hitattr_make(e.name, e.base, e.group, aseq+1, self.conf[e.name].extra_self)
        else:
            self.a_update_sigil(-60)

    def a_shift_sigil(self, t):
        self.a_update_sigil(-240)

variants = {None: Nevin}
