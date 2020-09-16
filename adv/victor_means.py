from core.advbase import *
from module.bleed import mBleed
from slot.d import *
from slot.a import *
from adv import victor

def module():
    return Victor

class Victor(victor.Victor):
    conf = victor.Victor.conf.copy()
    conf['mbleed'] = True
    def prerun(self):
        self.bleed = mBleed('g_bleed',0).reset()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(Victor, *sys.argv)