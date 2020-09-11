from core.advbase import *
from slot.a import *

def module():
    return Alfonse

class Alfonse(Adv):
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon
        `s3, cancel
        `s2, cancel
        `s4, cancel
        `s1, fsc or not self.afflics.paralysis.get()
        `fs, x=2
    """
    conf['coabs'] = ['Sharena','Lucretia','Peony']
    conf['share'] = ['Kleimann']	

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)