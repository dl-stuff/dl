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
    conf['afflict_res.frostbite'] = 0
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
        self.a1_buff.set(0.10*mrate)
        self.a1_buff.on()
        self.a1_stack = mrate - 1

    @property
    def buffcount(self):
        buffcount = super().buffcount
        return buffcount + self.a1_stack

        self.crit_mod = self.custom_crit_mod
        self.a1_cd = False

    def custom_crit_mod(self, name):
        if self.a1_cd or name == 'test':
            return self.solid_crit_mod(name)
        else:
            crit = self.rand_crit_mod(name)
            if crit > 1 and not self.a1_cd:
                Spdbuff('a1', 0.10, 20).on()
                self.a1_cd = True
                Timer(self.a1_cd_off).on(10)
            return crit

    def a1_cd_off(self, t):
        self.a1_cd = False


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)