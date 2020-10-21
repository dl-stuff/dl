from core.advbase import *

def module():
    return Forte

class Forte(Adv):
    def prerun(self):
        Event('s').listener(self.s_dgauge)

    def s_dgauge(self, e):
        if e.name != 'ds':
            self.dragonform.charge_gauge(40, dhaste=False)

variants = {None: Forte}

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
