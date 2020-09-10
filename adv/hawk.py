from core.advbase import *
from slot.a import *

def module():
    return Hawk

conf_fs_alt = {
    'fs_a.dmg': 4.94,
    'fs_a.hit':19,
    'fs_a.sp':2400,
    'fs_a.iv': 0.5
}
class Hawk(Adv):    
    conf = conf_fs_alt.copy()
    conf['slots.a'] = Resounding_Rendition()+The_Fires_of_Hate()
    conf['acl'] = """
        # queue self.duration<=60 and prep and self.afflics.stun.resist
        # s2; s3; fs; s1, fsc; fs; s1, fsc; s1, cancel; s2, cancel
        # end
        `s3, not self.s3_buff
        `dragon(c3-s-end), s and self.duration >= 120
        `s2, self.fs_alt.uses=0 or (self.s2_mode=1)
        `fs, (s1.check() and self.fs_alt.uses>1) or (x=4 and self.s2_mode=0 and self.fs_alt.uses>0)
        `s1, fsc or s=1
        `s4, s or x=5
    """

    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Sylas']
    conf['share'] = ['Curran']
    conf['afflict_res.stun'] = 80
    conf['afflict_res.poison'] = 0
    
    def fs_proc(self, e):
        if e.suffix == 'a':
            self.afflics.stun(e.name, 110)
            self.afflics.poison(e.name, 120, 0.582)

    def prerun(self):
        self.fs_alt = FSAltBuff(self, 'a', uses=2)
        self.s2_mode = 0
        self.a_s2 = self.s2.ac
        self.a_s2a = S('s2', Conf({'startup': 0.10, 'recovery': 2.5}))

    def s1_proc(self, e):
        with KillerModifier('s1_stun_killer', 'hit', 3.3, ['stun']):
            self.dmg_make(e.name,4.74)
        with KillerModifier('s1_poison_killer', 'hit', 2, ['poison']):
            self.dmg_make(e.name,4.74)

    def s2_proc(self, e):
        if self.s2_mode == 0:
            self.fs_alt.on()
            self.s2.ac = self.a_s2a
        else:
            with KillerModifier('s2_killer', 'hit', 0.5, ['poison']):
                self.dmg_make(e.name, 9.48)
            self.conf.s2.startup = 0.25
            self.conf.s2.recovery = 0.9
            self.s2.ac = self.a_s2
            self.add_hits(3)
        self.s2_mode = (self.s2_mode + 1) % 2


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
