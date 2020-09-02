from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Zardin

class Zardin(Adv):
    a1 = ('a',0.20,'hp100')
    
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+Primal_Crisis()
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon.act('c3 s c1 end'),s
        `s3
        `s4, cancel or (s2.check() and s1.check())
        `s2, fsc or s1.check()
        `s1, fsc
        `fs, x=2
        """
    conf['coabs'] = ['Blade', 'Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

    def s1_proc(self, e):
        self.afflics.frostbite(e.name,120,0.41)

    def s2_proc(self, e):
        self.afflics.frostbite(e.name,120,0.41)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)