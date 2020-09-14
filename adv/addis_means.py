from core.advbase import *
from adv import addis
from module.bleed import mBleed
from slot.a import *

def module():
    return Addis

class Addis(addis.Addis):
    conf = addis.Addis.conf.copy()
    conf['mbleed'] = True
    def prerun(self):
        super().prerun()
        self.bleed = mBleed('g_bleed',0).reset()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(Addis, *sys.argv)