from core.advbase import *

def module():
    return Ezelith

class Ezelith(Adv):
    a3 = ('bk',0.35)
    conf = {}
    conf['slots.d'] = 'Gala_Mars'
    conf['acl'] = """
        `dragon(c3-s-s-end),s=1
        `s3, not buff(s3)
        `s1
        `s4
        `s2
        `fs, x=5
        """
    conf['coabs'] = ['Halloween_Mym', 'Blade', 'Wand']
    conf['share'] = ['Summer_Patia']

    def s1_hit(self, name, base, group, aseq):
        self.a1_hits += 1
        if self.a1_hits % 2 == 0:
            Selfbuff('a1',0.2,7,'crit','chance').on()

    def prerun(self):
        self.a1_hits = 0
        for h in range(0, 12):
            setattr(self, f's1_hit{h}', self.s1_hit)

    def s2_chance(self):
        return 0.35 if self.hits >= 15 else 0.15

    def x_proc(self, e):
        if self.buff('s2'):
            Debuff('s2_ab', -0.05, 5, self.s2_chance()).on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)