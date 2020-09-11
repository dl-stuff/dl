from core.advbase import *
from slot.d import *
from slot.a import *

def module():
    return Ranzal

class Ranzal(Adv):
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end), s or x=5
        `s3, not buff(s3)
        `s1
        `s4
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Eleonora']
    conf['share'] = ['Curran']
    conf['afflict_res.poison'] = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
