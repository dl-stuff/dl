from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Karina

class Karina(Adv):
    conf = {}
    conf['slots.a'] = Summer_Paladyns()+Odd_Sparrows()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon(c3-s-end), s=1
        `s4
        `s3
        `s1
        `s2
        `fs, x=4 and (s1.charged>=s1.sp-self.sp_val('fs') or s2.charged>=s2.sp-self.sp_val('fs'))
    """

    conf['coabs'] = ['Tobias', 'Renee', 'Summer_Estelle']
    conf['share'] = ['Summer_Cleo', 'Patia']

    def prerun(self):
        self.set_hp(1)

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