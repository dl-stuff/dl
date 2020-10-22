from core.advbase import *

class Lathna(Adv):
    comment = 'cat sith skill damage does not work on s1 extra hits'

    def prerun(self):
        self.dragonform.shift_mods.append(Modifier('faceless_god', 'poison_killer', 'passive', 2.00).off())
    
    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.current_s[dst] = 'all'

    @allow_acl
    def s(self, n, s1_kind=None):
        if n == 1 and s1_kind == 'all':
            self.current_s['s1'] = s1_kind
        else:
            self.current_s['s1'] = 'default'
        return super().s(n)

    def s1_do_hit(self, t):
        # reeeeeee fix ur shit cykagames
        with KillerModifier('s1_killer', 'hit', 0.6, ['poison']):
            self.dmg_make(t.name, 2.61/(1 + self.sub_mod('s', 'buff')))
            self.add_combo(t.name)

    def s1_proc(self, e):
        if e.group != 'all':
            return
        for i in range(4):
            t = Timer(self.s1_do_hit)
            t.name = e.name
            t.on(i*0.4+0.4)

class Lathna_BUGFIX(Lathna):
    comment = 'if s1 aspd and sd buff bugs were fixed'
    conf = {
        's1_all': {
            'recovery': 4.05,
            'recovery_nospd': 0,
            'attr': [
                {'dmg': 2.61, 'killer': [1.0, ['poison']], 'iv': 0.66667},
                {'dmg': 2.61, 'killer': [1.0, ['poison']], 'iv': 1.0},
                {'dmg': 2.61, 'killer': [1.0, ['poison']], 'iv': 1.33333},
                {'dmg': 2.61, 'killer': [1.0, ['poison']], 'iv': 1.83333},
                {'dmg': 2.61, 'killer': [1.0, ['poison']], 'iv': 2.33333},
                {'dmg': 2.61, 'killer': [1.0, ['poison']], 'iv': 2.83333},
                {'dmg': 2.61, 'killer': [1.0, ['poison']], 'iv': 3.33333}
            ]
        }
    }

    # force use of s1_all cus im too lazy to fix acl
    @allow_acl
    def s(self, n, s1_kind=None):
        return super().s(n, s1_kind='all')

    def s1_proc(self, e):
        pass

variants = {
    None: Lathna,
    'BUGFIX': Lathna_BUGFIX
}
