from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Karina

class Karina(Adv):
    a1 = ('bc_regen', 1, 25)
    a3 = [('prep',1.00), ('scharge_all', 0.05)]

    conf = {}
    conf['slots.a'] = Valiant_Crown()+Felyne_Hospitality()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon.act('c3 s end'), s=1
        `s4
        `s3
        `s2
        `s1
    """

    conf['coabs'] = ['Tobias', 'Renee', 'Summer_Estelle']
    conf['share'] = ['Summer_Cleo', 'Patia']


    def s1_proc(self, e):
        boost = 0.05*self.buffcount
        log('debug', 'karina_s1_boost', f'x{self.buffcount} = {self.conf[e.name].dmg*(1+boost):.2%}')
        self.afflics.frostbite(e.name,120,0.41*(1+boost))
        self.dmg_make(f'o_{e.name}_boost',self.conf[e.name].dmg*boost)

    def s2_proc(self, e):
        Selfbuff(f'{e.name}_defense', 0.30, 30, 'defense').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)