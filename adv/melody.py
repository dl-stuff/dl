from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Melody

maido_fs = {'fs_oops.dmg': 3.40, 'fs_oops.recovery': 72 / 60}
class Melody(Adv):
    conf = maido_fs.copy()
    conf['slots.a'] = A_Dogs_Day()+From_Whence_He_Comes()
    conf['slots.d'] = Ariel()
    conf['acl'] = """
        `s3, not buff(s3)
        `s1
        `s4
        `fs, x=5
    """
    conf['coabs'] = ['Bow','Tobias','Dagger2']
    conf['share'] = ['Dragonyule_Xainfried']

    def prerun(self):
        self.fs_alt = FSAltBuff('oops', uses=1)

    def s1_proc(self, e):
        self.fs_alt.on()

    def s2_proc(self, e):
        self.afflics.poison(e.name, 120, 0.582)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)