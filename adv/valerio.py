from core.advbase import *
from module.template import StanceAdv, RngCritAdv
import random

def module():
    return Valerio


class Valerio(StanceAdv, RngCritAdv):
    conf = {}
    conf['slots.a'] = ['The_Wyrmclan_Duo', 'Primal_Crisis']
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = 'Siren'
    conf['acl'] = """
        `s3, not buff(s3) 
        `s2(entree), self.inspiration()=0
        `s2(dessert)
        `s4
        `s1(appetizer), buff.timeleft(s1, appetizer) < 7
        `s1(dessert)
    """
    conf['coabs'] = ['Summer_Estelle', 'Renee', 'Xander']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

    def prerun(self):
        self.config_stances({
            'appetizer': ModeManager(group='appetizer', x=True, s1=True, s2=True),
            'entree': ModeManager(group='entree', x=True, s1=True, s2=True),
            'dessert': ModeManager(group='dessert', x=True, s1=True, s2=True),
        }, hit_threshold=20)
    
    ### mass sim ###
    #     self.config_rngcrit(cd=10)
    # def rngcrit_cb(self):
    #     Selfbuff('a1', 0.10, 20, 'spd', 'passive').on()
    ### mass sim ###

        self.config_rngcrit(cd=10, ev=20)
        self.a1_buff = Selfbuff('a1', 0, 20, 'spd', 'passive')
        self.a1_stack = 0

    def rngcrit_cb(self, mrate=None):
        new_value = 0.10*mrate
        if not self.a1_buff:
            self.a1_buff.set(new_value)
            self.a1_buff.on()
        else:
            self.a1_buff.value(new_value)
        self.a1_stack = mrate - 1

    @property
    def buffcount(self):
        buffcount = super().buffcount
        return buffcount + self.a1_stack

    def a1_cd_off(self, t):
        self.a1_cd = False


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)