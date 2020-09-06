from core.advbase import *
from slot.a import *
from slot.d import *
from module.x_alt import Fs_alt

def module():
    return Vice

class Vice(Adv):
    a1 = ('bk',0.35)
    conf = {}
    conf['slots.a'] = Twinfold_Bonds()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3 s end), (fsc or self.sim_afflict) and self.trickery=0
        `s3, not self.s3_buff
        `s4
        `s1
        `s2
        `fs, x=5
        """
    conf['coabs'] = ['Wand','Gala_Alex','Ieyasu']
    conf['afflict_res.poison'] = 0
    conf['share'] = ['Curran']

    def fs_proc_alt(self, e):
        self.afflics.poison('fs', 120, 0.582)

    def prerun(self):
        conf_fs_alt = {'fs.dmg': 0.174, 'fs.hit': 6}
        self.fs_alt = Fs_alt(self, conf_fs_alt, self.fs_proc_alt)

    def s1_proc(self, e):
        with KillerModifier('s1_killer', 'hit', 0.5, ['poison']):
            self.dmg_make(e.name, 15.84)

    def s2_proc(self, e):
        self.fs_alt.on(1)
        with KillerModifier('s2_killer', 'hit', 0.5, ['poison']):
            self.dmg_make(e.name, 16.77)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
