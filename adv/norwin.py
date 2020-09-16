from core.advbase import *
from slot.a import *

def module():
    return Norwin

class Norwin(Adv):    
    conf = {}
    conf['slots.a'] = Forest_Bonds()+Primal_Crisis()
    conf['slots.poison.a'] = Forest_Bonds()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end), fsc
        `s3, not buff(s3)
        `s4
        `s1, cancel and buff(s3)
        `s2
        `fs,x=5
    """
    conf['coabs'] = ['Ieyasu','Wand','Forte']
    conf['share'] = ['Curran']
    conf['afflict_res.blind'] = 80


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
