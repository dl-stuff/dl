from core.advbase import *

def module():
    return Vida

conf_fs_alt = {'fs_a.dmg': 2.04, 'fs_a.hit': 6}
class Vida(Adv):
    comment = 'no s2'
    conf = conf_fs_alt.copy()
    conf['acl'] = """
        `dragon(c3-s-end), s or fsc
        `s3, not buff(s3) and x=5
        `s4
        `s1, cancel
        `fs, x=5
        """
    conf['coabs'] = ['Ieyasu','Wand','Forte']
    conf['share'] = ['Kleimann']

    def d_coabs(self):
        if self.sim_afflict:
            self.conf['share'] = ['Curran']

    def prerun(self):
        self.fs_alt = FSAltBuff('a', uses=3)

    def s2_proc(self, e):
        self.fs_alt.on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
