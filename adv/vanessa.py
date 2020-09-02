from core.advbase import *
from slot.a import *

def module():
    return Vanessa

class Vanessa(Adv):
    a1 = ('fs',0.4)
    a3 = ('lo',0.3)
    
    conf = {}
    conf['slots.a'] = Summer_Paladyns()+Primal_Crisis()
    conf['slots.burn.a'] = Resounding_Rendition()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon, s
        `s3, not self.s3_buff
        `s4, cancel
        `s1, cancel
        `s2, fsc
        `fs, x=4
    """
    conf['coabs'] = ['Blade', 'Marth', 'Wand']
    conf['share'] = ['Kleimann']

    def d_coabs(self):
        if self.sim_afflict:
            self.conf['coabs'] = ['Blade','Marth','Wand']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
