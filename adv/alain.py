from core.advbase import Adv
from core.ability import Last_Buff

class Alain(Adv):
    def prerun(self):
        Last_Buff.HEAL_TO = 50

variants = {None: Alain}

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
