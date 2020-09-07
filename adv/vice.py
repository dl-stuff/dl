from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Vice

conf_fs_alt = {'fs_a.dmg': 0.174, 'fs_a.hit': 6}
class Vice(Adv):
    conf = conf_fs_alt.copy()
    conf['slots.a'] = Twinfold_Bonds()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end), (fsc or self.sim_afflict) and self.trickery=0
        `s3, not self.s3_buff
        `s4
        `s1
        `s2
        `fs, x=5
        """
    conf['coabs'] = ['Wand','Gala_Alex','Ieyasu']
    conf['afflict_res.poison'] = 0
    conf['share'] = ['Curran']

    def fs_proc(self, e):
        if e.group == 'a':
            self.afflics.poison('fs', 120, 0.582)

    def prerun(self):
        self.fs_alt = FSAltBuff(self, 'a', uses=1)

    def s2_proc(self, e):
        self.fs_alt.on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
