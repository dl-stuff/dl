from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Althemia

class Althemia(Adv):    
    conf = {}
    conf['slots.a'] = Candy_Couriers()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end), x=5
        `s3, not buff(s3)
        `s2
        `s4
        `s1,buff(s3) and cancel
    """
    conf['coabs'] = ['Gala_Alex','Delphi','Bow']
    conf['share'] = ['Curran']
    conf['afflict_res.poison'] = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
