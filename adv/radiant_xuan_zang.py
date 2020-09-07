from core.advbase import *
from slot.d import *
from slot.a import *

def module():
    return Radiant_Xuan_Zang

staff_fs_conf = {
    'fs.dmg': 0.61*4,
    'fs_xihe.dmg': 8.88,
    'fs.sp': 580,
    'fs.charge': 24 / 60.0,
    'fs.startup': 100 / 60.0,
    'fs.recovery': 40 / 60.0,
    'fs.hit': 4,

    'fs.x1.charge': 33 / 60.0, # 9 delay + FS
    'fs.x2.charge': 30 / 60.0, # 6 delay + FS
}

class Radiant_Xuan_Zang(Adv):
    conf = staff_fs_conf.copy()
    conf['slots.a'] = Candy_Couriers()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon, cancel
        `s3, not self.s3_buff
        `s1
        `s2
        `s4, x>2
        `fs, self.fs_alt.uses>0 and x=4
    """
    conf['coabs'] = ['Sharena', 'Blade', 'Peony']
    conf['share'] = ['Summer_Patia']
    conf['afflict_res.paralysis'] = 0

    def fs_proc(self, e):
        if e.suffix == 'xihe':
            self.afflics.paralysis.res_modifier = 0.20
            Timer(self.paralysis_rate_reset).on(20)

    def paralysis_rate_reset(self, t):
        self.afflics.paralysis.res_modifier = 0

    def prerun(self):
        self.fs_alt = FSAltBuff(self, 'xihe', uses=1)
        self.xihe_gauge = 0
        self.xihe = {'s1': False, 's2': False}
        if self.condition('buff all team'):
            self.xihe_gauge_gain = 50
            self.buff_class = Teambuff
        else:
            self.xihe_gauge_gain = 20
            self.buff_class = Selfbuff

    def s1_proc(self, e):
        if self.xihe[e.name]:
            self.xihe[e.name] = False
            with KillerModifier('s1_killer', 'hit', 0.5, ['paralysis']):
                self.dmg_make(e.name, 18.80)
            Debuff(e.name, 0.25, 10, 1, 'attack').on()
        else:
            self.dmg_make(e.name, 16.1)
            Debuff(e.name, 0.10, 10, 0.70, 'attack').on()
            self.afflics.paralysis(e.name,120,0.97)

    def s2_proc(self, e):
        if self.xihe[e.name]:
            self.xihe[e.name] = False
            self.buff_class(e.name, 0.20, 15).on()
            self.inspiration.add(5, team=True)
        else:
            self.xihe_gauge += self.xihe_gauge_gain
            log('debug', 'xihe', self.xihe_gauge)
            if self.xihe_gauge >= 100:
                self.xihe_gauge = 0
                self.fs_alt.on()
                self.xihe = {'s1': True, 's2': True}

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)