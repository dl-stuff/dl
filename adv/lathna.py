from core.advbase import *

class Lathna(Adv):
    def prerun(self):
        self.dragonform.shift_mods.append(Modifier('faceless_god', 'poison_killer', 'passive', 2.00).off())
        Event('dragon').listener(self.dshift_heal)
    
    def dshift_heal(self, e):
        Selfbuff('lathna_regen', 14, 20, 'regen', 'buff', source='dshift').on()

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.current_s[dst] = 'all'

    @allow_acl
    def s(self, n, s1_kind=None):
        if n == 1 and s1_kind == 'all':
            self.current_s['s1'] = 'all'
        else:
            self.current_s['s1'] = 'default'
        return super().s(n)

class Lathna_BUGFIX(Lathna):
    comment = 'if s1 aspd bug was fixed'
    conf = {
        's1_all': {
            'recovery': 4.05,
            'recovery_nospd': 0,
        }
    }

    # # force use of s1_all cus im too lazy to fix acl
    # @allow_acl
    # def s(self, n, s1_kind=None):
    #     return super().s(n, s1_kind='all')

    def s1_proc(self, e):
        pass

variants = {
    None: Lathna,
    'BUGFIX': Lathna_BUGFIX
}
