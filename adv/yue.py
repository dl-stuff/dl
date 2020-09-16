from core.advbase import *
from slot.a import *

def module():
    return Yue

class Yue(Adv):
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Breakfast_at_Valerios()
    conf['slots.burn.a'] = Kung_Fu_Masters()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon, s=2
        `s3, not buff(s3)
        `s2,x=5
        `s4,cancel
        `s1,cancel
        """
    conf['coabs'] = ['Blade', 'Marth', 'Halloween_Mym']
    conf['share'] = ['Kleimann']

    def d_coabs(self):
        if self.duration <= 60:
            self.conf['coabs'] = ['Yuya','Marth','Halloween_Mym']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
