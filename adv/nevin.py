from core.advbase import *
from module.template import SigilAdv

def module():
    return Nevin

class Nevin(SigilAdv):
    conf = {}
    conf['slots.d'] = 'Ramiel'
    conf['slots.a'] = ['Twinfold_Bonds', 'The_Red_Impulse']
    conf['slots.poison.a'] = ['Twinfold_Bonds', 'The_Plaguebringer']
    conf['acl'] = """
        `s3, not buff(s3)
        `s1
        `s2, cancel
        if not self.unlocked
        `dragon(c3-s-end)
        else
        `dragon(c3-s-end)
        `s4, x=6
        `fsf, x=6
        end
        """
    conf['coabs'] = ['Berserker','Ieyasu','Forte']
    conf['share'] = ['Veronica']

    def prerun(self):
        # alt s1 doesn't add dps
        self.config_sigil(duration=300, x=True, s2=True)
        self.zone = ZoneTeambuff()

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
            for aseq in range(len(self.zone.zone_buffs)):
                self.hitattr_make(e.name, e.base, e.group, aseq+1, self.conf[e.name].extra_self)
        else:
            self.a_update_sigil(-60)

    def a_shift_sigil(self, t):
        self.a_update_sigil(-240)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
