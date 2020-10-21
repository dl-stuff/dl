from core.advbase import *

def module():
    return Grace

class Grace(Adv):
    def prerun(self):
        self.hp = 100

variants = {None: Grace}

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
