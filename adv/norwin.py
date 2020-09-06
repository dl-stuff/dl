from core.advbase import *
from slot.a import *

def module():
    return Norwin

class Norwin(Adv):
    a1 = ('affteam_blind', 0.10, 10, 5)
    a3 = ('k_blind', 0.20)
    
    conf = {}
    conf['slots.a'] = Forest_Bonds()+Primal_Crisis()
    conf['slots.poison.a'] = Forest_Bonds()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3 s end), fsc
        `s3, not self.s3_buff
        `s4
        `s1, cancel and self.s3_buff
        `s2
        `fs,x=5
    """
    conf['coabs'] = ['Ieyasu','Wand','Forte']
    conf['share'] = ['Curran']
    conf['afflict_res.blind'] = 80

    def s1_proc(self, e):
        self.afflics.blind(e.name,100)

    def s2_proc(self, e):
        with KillerModifier('s2_killer', 'hit', 0.44, ['blind']):
            self.dmg_make(e.name,3*2.45)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
