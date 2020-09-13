from core.advbase import *
from slot.a import *

def module():
    return Eleonora

class Eleonora(Adv):
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end)
        `s3, not buff(s3)
        `s1, fsc
        `s2, fsc
        `s4, fsc
        `fs, seq=4
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']
    conf['afflict_res.poison'] = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)