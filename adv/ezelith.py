from core.advbase import *

def module():
    return Ezelith

class Ezelith(Adv):
    conf = {}
    conf['slots.a'] = [
    'Twinfold_Bonds',
    'Flash_of_Genius',
    'Moonlight_Party',
    'A_Passion_for_Produce',
    'His_Clever_Brother'
    ]
    conf['slots.burn.a'] = [
    'Twinfold_Bonds',
    'Me_and_My_Bestie',
    'Flash_of_Genius',
    'Chariot_Drift',
    'His_Clever_Brother'
    ]
    conf['slots.d'] = 'Gala_Mars'
    conf['acl'] = """
        `dragon, (s=1 and not s4.check())
        `s3, not buff(s3)
        `s2
        `s1
        `s4, s=1
        `fs, x=5
        """
    conf['coabs'] = ['Halloween_Mym', 'Blade', 'Wand']
    conf['share'] = ['Xander']

    def s1_hit(self, name, base, group, aseq):
        self.a1_hits += 1
        if self.a1_hits % 2 == 0:
            Selfbuff('a1',0.2,7,'crit','chance').on()

    def prerun(self):
        self.a1_hits = 0
        for h in range(0, 12):
            setattr(self, f's1_hit{h}', self.s1_hit)

    def s2_chance(self):
        return 0.55 if self.hits >= 15 else 0.35

    def x_proc(self, e):
        if self.buff('s2'):
            Debuff('s2_ab', -0.10, 5, self.s2_chance()).on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)