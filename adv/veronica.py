from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Veronica

class Veronica(Adv):
    comment = 'last destruction team DPS not considered'
    conf = {}
    conf['slots.a'] = Candy_Couriers()+Primal_Crisis()
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = """
        `dragon(c3-s-end), ((self.hp>0 and s) or (self.hp=0 and x=5))
        queue prep and not buff(s3)
        `s3;s4;s2;s1
        end
        `s1
        `s4
        """
    conf['coabs'] = ['Berserker','Curran','Summer_Patia']
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Curran']

    def prerun(self):
        # Teambuff('last',2.28,1).on()
        self.a1_buff = Selfbuff('a1', 0.30, -1, 's', 'buff')
        Event('hp').listener(self.a1_buff_on)

    def a1_buff_on(self, e):
        # assume you take bit more damage at and proc last destruction at some point
        if e.hp <= 50 and not self.a1_buff.get():
            self.set_hp(30)
            self.a1_buff.on()

    # def s1_proc(self, e):
    #     if self.hp >= 50:
    #         self.set_hp(self.hp-10)
    #         self.charge_p(f'{e.name}_hpcut', 0.20, target=e.name)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
