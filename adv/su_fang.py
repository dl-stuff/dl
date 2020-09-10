from core.advbase import *
from slot.a import *

def module():
    return Su_Fang

conf_fs_alt = {'fs_a.dmg': 0.174, 'fs_a.hit': 6}

class Su_Fang(Adv):
    conf = conf_fs_alt.copy()
    conf['slots.a'] = Twinfold_Bonds()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end),s4.check()
        `s3, not self.s3_buff
        `s4
        `s1, cancel and self.s3_buff 
        `s2, fsc
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']

    def fs_proc(self, e):
        if e.suffix == 'a':
            self.afflics.poison('fs', 120, 0.582)

    def prerun(self):
        self.fs_alt = FSAltBuff(self, 'a', uses=1)
        self.s2_buff = Selfbuff('s2', 0.30, 15)

    def s1_proc(self, e):
        with KillerModifier('skiller', 'hit', 0.50, ['poison']):
            self.dmg_make(e.name, 5.58)
            if self.s2_buff.get():
                self.dmg_make(e.name, 2.60)
                self.add_hits(2)

    def s2_proc(self, e):
        self.fs_alt.on()
        self.s2_buff = Selfbuff(e.name, 0.30, 15).on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
