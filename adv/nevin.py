from core.advbase import *
from slot.a import *
from slot.d import *

nevin_conf = {
    'fs.dmg': 0,

    'x6.dmg': 0,
    'x6.sp': 0,
    'x6.startup': 2 / 60.0,
    'x6.recovery': 0,
    'x6.hit': 0,
} # get real frames 1 day, maybe

def module():
    return Nevin

class Nevin(Adv):
    a3 = ('cd', 0.20)

    conf = nevin_conf.copy()
    conf['slots.d'] = Ramiel()
    conf['slots.a'] = Twinfold_Bonds()+The_Red_Impulse()
    conf['slots.poison.a'] = Twinfold_Bonds()+The_Plaguebringer()
    conf['acl'] = """
        `s3, not self.s3_buff
        `s1
        `s2, cancel
        if not self.unlocked
        `dragon.act('c3 s end'), x=5
        `s4, x=5
        else
        `dragon.act('c3 s end'), x=6
        `s4, x=6
        end
        """
    conf['coabs'] = ['Berserker','Ieyasu','Forte']
    conf['afflict_res.poison'] = 0
    conf['share'] = ['Veronica']

    def init(self):
        self.x_max = 6

    def prerun(self):
        self.x_max = 5
        self.unlocked = False
        self.sigil = EffectBuff('locked_sigil', 300, lambda: None, self.unlock).no_bufftime()
        self.sigil.on()
        t = Timer(self.sword_dmg, 1.5, True)
        self.sword = EffectBuff('revelation_sword', 12, lambda: t.on(), lambda: t.off()).no_bufftime()
        Event('dragon').listener(self.shift_sigil)

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.unlocked = True
        adv.rebind_function(Nevin, 'buff_zone_count')

    def unlock(self):
        self.x_max = 6
        self.unlocked = True

    def buff_zone_count(self):
        return min(4, len([b for b in self.all_buffs if 'zone' in b.name and b.get()]))

    def sword_dmg(self, e):
        self.dmg_make('#revelation_sword', 4.00, '#')
        self.add_hits(4)

    def x_proc(self, e):
        if self.unlocked and e.name == 'x6':
            self.set_hp(self.hp*0.9)
            self.sword.on()

    def s1_proc(self, e):
        if self.condition(f'{e.name} buff for 10s'):
            Teambuff(e.name,0.25,10).zone().on()
            # unlocked -> light res

    def update_sigil(self, time):
        duration = self.sigil.buff_end_timer.add(time)
        if duration <= 0:
            self.sigil.off()
            self.unlock()

    def s2_proc(self, e):
        if self.unlocked:
            for _ in range(self.buff_zone_count()):
                self.dmg_make(e.name, 3.00)
                self.add_hits(1)
            # 1.00 for ally buff zones
        else:
            self.update_sigil(-60)

    def shift_sigil(self, t):
        self.update_sigil(-240)
            

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
