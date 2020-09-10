from core.advbase import *
from adv import addis
from module.bleed import mBleed
from slot.a import *

def module():
    return Addis

class Addis(addis.Addis):
    def prerun(self):
        super().prerun()
        self.bleed = mBleed('g_bleed',0).reset()

    def s1_proc(self, e):
        if e.group == 'enhanced':
            mBleed(e.name, 1.32).on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(Addis, *sys.argv)