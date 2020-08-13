from core.advbase import *
from slot.a import *

def module():
    return Yue

class Yue(Adv):
    a1 = ('lo_defense', 0.60)

    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Breakfast_at_Valerios()
    conf['slots.burn.a'] = Kung_Fu_Masters()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon, s=2
        `s3, not self.s3_buff
        `s2
        `s4
        `s1
    """
    coab = ['Blade', 'Dagger2', 'Halloween_Mym']
    share = ['Ranzal']

    def d_coabs(self):
        if self.duration <= 60:
            self.coab = ['Blade','Marth','Dagger2']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
