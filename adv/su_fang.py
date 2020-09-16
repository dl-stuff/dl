from core.advbase import *
from slot.a import *

def module():
    return Su_Fang

class Su_Fang(Adv):
    conf = {}
    conf['slots.a'] = Twinfold_Bonds()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end),s4.check()
        `s3, not buff(s3)
        `s4
        `s1, cancel and buff(s3) 
        `s2, fsc
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
