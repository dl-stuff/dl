from core.advbase import *

def module():
    return Halloween_Melsa

class Halloween_Melsa(Adv):
    pass

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)