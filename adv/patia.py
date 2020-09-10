from core.advbase import *
from module.bleed import Bleed
from slot.a import *
from slot.d import *

def module():
    return Patia

class Patia(Adv):
    conf = {}
    conf['slots.a'] = Proper_Maintenance()+FWHC()
    conf['slots.poison.a'] = conf['slots.a']
    conf['slots.d'] = Azazel()
    conf['acl'] = """
        `dragon(c3-s-end), fsc
        `s3, not self.s3_buff
        `s1
        `s4, x=5
        `fs, x=5
    """

    conf['coabs'] = ['Audric','Bow','Tobias']
    conf['share'] = ['Karl']

    def prerun(self):
        self.bleed = Bleed('g_bleed',0).reset()

    def s1_proc(self, e):
        Teambuff(f'{e.name}_defense', 0.25, 15, 'defense').on()

    def s2_proc(self, e):
        Bleed(e.name, 1.46).on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
