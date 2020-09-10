from core.advbase import *
from slot.a import *

def module():
    return Alain

class Alain(Adv):
    a1 = ('lo_defense', 1.00)

    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon, s=2
        `s3, not self.s3_buff
        `s1, cancel
        `s2, cancel
        `s4, cancel
        `fs, x=5
        """
    conf['afflict_res.burn'] = 0
    conf['coabs'] = ['Blade', 'Wand', 'Marth']
    conf['share'] = ['Kleimann']

    def s1_proc(self, e):
        self.afflics.burn(e.name,100,0.803)
    
    def s2_proc(self, e):
        self.afflics.burn(e.name,100,0.803)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
