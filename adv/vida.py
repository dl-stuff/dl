from core.advbase import *
from module.x_alt import Fs_alt

def module():
    return Vida

class Vida(Adv):
    comment = 'no s2'
    a1 = ('fs',0.30)
    conf = {}
    conf['acl'] = """
        `dragon.act('c3 s end'), s or fsc
        `s3, not self.s3_buff and x=5
        `s4
        `s1, cancel
        `fs, x=5
        """
    coab = ['Ieyasu','Wand','Forte']
    share = ['Curran']

    def prerun(self):
        conf_fs_alt = {'fs.dmg': 2.04, 'fs.hit': 6}
        self.fs_alt = Fs_alt(self, Conf(conf_fs_alt))

    def s2_proc(self, e):
        self.fs_alt.on(3)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
