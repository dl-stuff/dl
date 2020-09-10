from core.advbase import *
from slot.d import *
from slot.a import *

def module():
    return Ranzal

class Ranzal(Adv):
    a1 = ('a', 0.08, 'hit15')
    a3 = [('lo_defense', 0.70),('lo_defense', 0.10, -1)]

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
    
    def s1_proc(self, e):
        self.afflics.poison(e.name, 120, 0.582)

    def s2_proc(self, e):
        Teambuff(e.name+'_defense', 0.25, 15, 'defense').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
