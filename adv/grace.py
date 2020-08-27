from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Grace

class Grace(Adv):
    a1 = ('fs',0.30)

    conf = {}
    conf['slots.a'] = The_Lurker_in_the_Woods()+Dear_Diary()
    conf['slots.d'] = Epimetheus()
    conf['acl'] = """
        `dragon
        `s3, not self.s3_buff
        `s4, fsc
        `dodge, fsc
        `fs, x=1
    """
    coab = ['Ieyasu', 'Dagger', 'Forte']
    share = ['Karl']

    def prerun(self):
        conf_fs_alt = {
            'fs.dmg': 382 / 100.0,
            'fs.sp': 800,
            'fs.charge': 1.7999999523162842,
            'fs.startup': 0.7333333492279053,
            'fs.recovery': 0.6,
            'fs.hit': -1,
        }
        self.conf += Conf(conf_fs_alt)
        self.hp = 100
        def healing_doublebuff_iv(e):
            buff = self.Timer(lambda t: self.set_hp(self.hp+4), 3.9, True)
            self.Timer(lambda t: buff.off()).on(20*self.buff.bufftime())
        self.Event('defchain').listener(healing_doublebuff_iv)

    def s1_proc(self, e):
        if self.hp >= 40:
            self.set_hp(30)
        else:
            Teambuff(e.name+'_defense', 0.30, 15, 'defense').on()

    def s2_proc(self, e):
        Teambuff(e.name+'_defense', 1.0, 5, 'defense').on()

    def fs_proc(self, e):
        self.set_hp(self.hp+5)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
