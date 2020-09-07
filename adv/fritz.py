from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Fritz

fritz_fs = {
    'fs_stun': {
        'dmg': 4.03,
        'hit': 11
    }
}

class Fritz(Adv):
    conf = fritz_fs.copy()
    conf['slots.a'] = Twinfold_Bonds()+The_Red_Impulse()
    conf['acl'] = """
        `dragon
        `s3
        `s1
        `s4, cancel
        `s2, x=5
        `fs, x=5
        """
    conf['coabs'] = ['Cleo','Raemond','Peony']
    conf['share'] = ['Kleimann']

    def fs_proc(self, e):
        if e.group == 'stun':
            self.afflics.stun('fs', 100)

    def prerun(self):
        self.fs_alt = FSAltBuff(self, 'stun', uses=3)

    def s2_proc(self, e):
        self.fs_alt.on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)