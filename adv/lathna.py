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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conf.s1_all.recovery = self.conf.s1.recovery + self.conf.s1_all.recovery_nospd
        self.conf.s1_all.recovery_nospd = 0
        self.conf.s1_all.attr = self.conf.s1.attr
        tmp_attr = self.conf.s1.attr[-1].copy()
        for _ in range(4):
            tmp_attr['iv'] += 0.4
            self.conf.s1_all.attr.append(tmp_attr.copy())

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
