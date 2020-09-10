from core.advbase import *
from slot.a import *

def module():
    return Luca

class Luca(Adv):
    conf = {}
    conf['slots.a'] = Forest_Bonds()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon, s=1
        `s3, not buff(s3) and fsc
        `s2, cancel
        `s4, cancel
        `s1, x>2 or fsc
        `fs, x=5
        """
    conf['coabs'] = ['Sharena','Lucretia','Peony']
    conf['share'] = ['Summer_Patia']
    conf['afflict_res.paralysis'] = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)