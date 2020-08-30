from core.advbase import *
from slot.a import *

def module():
    return Malora

class Malora(Adv):
    a1 = ('bk',0.2)
    
    conf = {}
    conf['slots.a'] = Forest_Bonds()+The_Red_Impulse()
    conf['slots.paralysis.a'] = Resounding_Rendition()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon
        `s4
        `s1
        `s2
        `s3
        `fs, x=5
        """
    coab = ['Cleo','Raemond','Peony']
    share = ['Summer_Patia']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)