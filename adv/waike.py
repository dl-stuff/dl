from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Waike

class Waike(Adv):
    a1 = ('edge_bog', 40, 'hp100')

    conf = {}
    conf['slots.a'] = Forest_Bonds()+Primal_Crisis()
    conf['slots.frostbite.a'] = Forest_Bonds()+His_Clever_Brother()
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon.act('c3 s end')
        `s3
        `s4
        `s1, cancel
        `s2, cancel
        `fs, seq=4
        """
    conf['coabs'] = ['Blade', 'Xander', 'Summer_Estelle']
    conf['afflict_res.bog'] = 100
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

    def s2_proc(self, e):
        self.afflics.bog.on(e.name, 80)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
