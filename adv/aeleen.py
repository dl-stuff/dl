from core.advbase import *
from slot.d import *
from slot.a import *

def module():
    return Aeleen

class Aeleen(Adv):
    a1 = ('bt',0.25)
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Breakfast_at_Valerios()
    conf['acl'] = """
        `dragon(c3-s-end), s4.check()
        `s3, not buff(s3)
        `s4
        `s1, buff(s3)
        `fs, seq=5
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
