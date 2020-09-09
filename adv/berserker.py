from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Berserker

class Berserker(Adv):
    a3 = ('lo',0.3)
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+Primal_Crisis()
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = """
        `dragon(c3-s-end),fsc
        `s3, not buff(s3) and fsc
        `s4
        `s1, cancel
        `fs, x=2
        """
    conf['coabs'] = ['Berserker','Ieyasu','Wand','Curran']
    conf['share'] = ['Kleimann']

    def d_coabs(self):
        if self.sim_afflict:
            self.conf['share'] = ['Curran']

    def s1_proc(self, e):
        Debuff(e.name, 0.05, 10, 0.4, 'attack')

    def s2_proc(self, e):
        self.buff_max_hp(f'{e.name}_hp', 0.10)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
