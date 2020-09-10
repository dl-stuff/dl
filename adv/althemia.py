from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Althemia

class Althemia(Adv):
    a1 = ('s',0.45,'hp100')
    
    conf = {}
    conf['slots.a'] = Candy_Couriers()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end), s=4
        `s3, not buff(s3)
        `s2
        `s4
        `s1,buff(s3) and cancel
    """
    conf['coabs'] = ['Ieyasu','Delphi','Gala_Alex']
    conf['afflict_res.poison'] = 0
    conf['share'] = ['Curran']

    def s1_proc(self, e):
        self.afflics.poison(e.name,100,0.482)

    def s2_proc(self, e):
        with KillerModifier('s2_killer', 'hit', 0.5, ['poison']):
            self.dmg_make(e.name, 14.96)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
