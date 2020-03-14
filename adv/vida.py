from core.advbase import *
from slot.a import *
from slot.d import *
from module.x_alt import Fs_alt

def module():
    return Vida

class Vida(Adv):
    a1 = ('fs',0.30)
    conf = {}
    conf['slot.a'] = Twinfold_Bonds()+The_Lurker_in_the_Woods()
    conf['slot.d'] = Fatalis()
    conf['acl'] = """
        `s3, not this.s3_buff
        `s1
        `s2
        `fs, x=2
        """

    def prerun(self):
        conf_fs_alt = {'fs.dmg': 0.110, 'fs.hit': 6}
        self.fs_alt = Fs_alt(self, Conf(conf_fs_alt))

    def s2_proc(self, e):
        self.fs_alt.on(3)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
