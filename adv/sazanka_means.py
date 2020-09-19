from core.advbase import *
from adv import sazanka
from module.bleed import mBleed

def module():
    return Sazanka

class Sazanka(sazanka.Sazanka):
    conf = sazanka.Sazanka.conf.copy()
    conf['mbleed'] = True
    def prerun(self):
        self.bleed = mBleed('g_bleed',0).reset()

if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)
