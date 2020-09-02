from core.advbase import *
from slot.a import *

def module():
    return Francesca

class Francesca(Adv):
    a1 = ('fs',0.30)
    conf = {}
    conf['slots.a'] = Twinfold_Bonds()+Primal_Crisis()
    conf['acl'] = """
        `dragon.act("c3 s end"), s4.check()
        `s3, not self.s3_buff
        `s4
        `s2
        `s1, cancel
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)