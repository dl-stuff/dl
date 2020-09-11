from core.advbase import *
from slot.a import *
from slot.d import *
from module.template import StanceAdv
import random

def module():
    return Valerio


valerio_conf = {
    # Valerio's Dessert Combo:
    # Total: 274
    # Total (No Recovery): 205
    # C1: 29
    # C2A: 86
    # C2B: 16
    # C2C: 8
    # C2D: 4
    # C3: 62
    # Recovey: 69

    # Dessert Stance
    # mC1 1 hit 195% 350SP (1.041s startup to cancel into mC2)
    # mC2 4 hits 27% 710SP (uses same Absorb effect as Axe C4, 1.73333s to cancel into mC3)
    # mc3 1 hit 453% 1590SP (cancelled @1.1573s)

    # C1 A
    'x1_dessert.dmg': 195 / 100.0,
    'x1_dessert.sp': 350,
    'x1_dessert.startup': 29 / 60.0,
    'x1_dessert.recovery': 0 / 60.0,
    'x1_dessert.hit': 1,

    # C2 A B C D
    'x2_dessert.dmg': 27 / 100.0,
    'x2_dessert.sp': 710,
    'x2_dessert.startup': 86 / 60.0,
    'x2_dessert.recovery': 0 / 60.0,
    'x2_dessert.hit': 1,

    'x3_dessert.dmg': 27 / 100.0,
    'x3_dessert.sp': 0,
    'x3_dessert.startup': 16 / 60.0,
    'x3_dessert.recovery': 0 / 60.0,
    'x3_dessert.hit': 1,

    'x4_dessert.dmg': 27 / 100.0,
    'x4_dessert.sp': 0,
    'x4_dessert.startup': 8 / 60.0,
    'x4_dessert.recovery': 0 / 60.0,
    'x4_dessert.hit': 1,

    'x5_dessert.dmg': 27 / 100.0,
    'x5_dessert.sp': 0,
    'x5_dessert.startup': 4 / 60.0,
    'x5_dessert.recovery': 0 / 60.0,
    'x5_dessert.hit': 1,

    # C3 A
    'x6_dessert.dmg': 453 / 100.0,
    'x6_dessert.sp': 1590,
    'x6_dessert.startup': 62 / 60.0,
    'x6_dessert.recovery': 69 / 60.0,
    'x6_dessert.hit': 1,

    # Valerio's Entree Combo:
    # Total: 269
    # Total (No Recovery): 203
    # C1: 29
    # C2A: 66
    # C2B: 15
    # C2C: 22
    # C3A: 57 (x4_entree hits)
    # C3B: 8 (x4_entree hits)
    # C3C: 6 (x4_entree hits)
    # Recovery (from C3C hit, I'm not sure if C3 is a projectile as a whole or not): 66

    # Entree Stance
    # mC1 1 hit 195% 350SP  (1.041s startup to cancel into mC2)
    # mC2 3 hits 162% 700SP  (1.0185s startup to cancel into mC3)
    # mc3 12 bullets 38% 720SP Attenuation rate 1.0 hitinterval 0.5, 0 Additional collisions (signaldata sent @1.6s forced cancel @2s)

    # C1 A
    'x1_entree.dmg': 195 / 100.0,
    'x1_entree.sp': 350,
    'x1_entree.startup': 29 / 60.0,
    'x1_entree.recovery': 0 / 60.0,
    'x1_entree.hit': 1,

    # C2 A B C
    'x2_entree.dmg': 162 / 100.0,
    'x2_entree.sp': 700,
    'x2_entree.startup': 66 / 60.0,
    'x2_entree.recovery': 0 / 60.0,
    'x2_entree.hit': 1,

    'x3_entree.dmg': 162 / 100.0,
    'x3_entree.sp': 0,
    'x3_entree.startup': 15 / 60.0,
    'x3_entree.recovery': 0 / 60.0,
    'x3_entree.hit': 1,

    'x4_entree.dmg': 162 / 100.0,
    'x4_entree.sp': 0,
    'x4_entree.startup': 22 / 60.0,
    'x4_entree.recovery': 0 / 60.0,
    'x4_entree.hit': 1,

    # C3 A B C
    'x5_entree.dmg': 152 / 100.0,
    'x5_entree.sp': 720,
    'x5_entree.startup': 57 / 60.0,
    'x5_entree.recovery': 0 / 60.0,
    'x5_entree.hit': 4,

    'x6_entree.dmg': 152 / 100.0,
    'x6_entree.sp': 0,
    'x6_entree.startup': 8 / 60.0,
    'x6_entree.recovery': 0 / 60.0,
    'x6_entree.hit': 4,

    'x7_entree.dmg': 152 / 100.0,
    'x7_entree.sp': 0,
    'x7_entree.startup': 6 / 60.0,
    'x7_entree.recovery': 66 / 60.0,
    'x7_entree.hit': 4,

    # Valerio's Appetizer Combo:
    # C1: 29
    # C2A: 56 (x2_appetizer hits) (High Damage)
    # C2B: 6 (x4_appetizer hits) (Two High Damage, Two Low)
    # C2C: 6 (x4_appetizer hits) (Low Damage)
    # C2D: 24 (x4_appetizer hits) (Low Damage)
    # C2E: 6 (x4_appetizer hits) (Low Damage)
    # C2F: 6 (x4_appetizer hits) (Low Damage)
    # C3A: 46
    # C3B: 99
    # C3C: 4
    # C3D: 4
    # Recovery (from C3D, idk if C3 is a projectile or not): 9

    # Appetiser stance
    # mC1 1 hit 195% 350SP (1.041s statup to cancel into mC2)
    # mC2 4 hit 129%  + 18 bullets 6% 680SP (1.0256s startup to cancel into mC3)
    # mC3 1 hit 143% (@0.4s) + 1 hit 143% (@2.067s) + 1 hit 143% (@2.13s) + 1 hit 143% (@2.2s) can end mC3 any time between 0.433333s and 2.067s by doing ANYTHING  1030SP (forced cancel at 2.267s)

    # C1 A
    'x1_appetizer.dmg': 195 / 100.0,
    'x1_appetizer.sp': 350,
    'x1_appetizer.startup': 29 / 60.0,
    'x1_appetizer.recovery': 0 / 60.0,
    'x1_appetizer.hit': 1,

    # C2 A B CDEF
    'x2_appetizer.dmg': 258 / 100.0,
    'x2_appetizer.sp': 680,
    'x2_appetizer.startup': 56 / 60.0,
    'x2_appetizer.recovery': 0 / 60.0,
    'x2_appetizer.hit': 2,

    'x3_appetizer.dmg': (258+12) / 100.0,
    'x3_appetizer.sp': 0,
    'x3_appetizer.startup': 6 / 60.0,
    'x3_appetizer.recovery': 0 / 60.0,
    'x3_appetizer.hit': 4,

    'x4_appetizer.dmg': 24 / 100.0,
    'x4_appetizer.sp': 0,
    'x4_appetizer.startup': 6 / 60.0,
    'x4_appetizer.recovery': 0 / 60.0,
    'x4_appetizer.hit': 4,

    'x5_appetizer.dmg': 24 / 100.0,
    'x5_appetizer.sp': 0,
    'x5_appetizer.startup': 24 / 60.0,
    'x5_appetizer.recovery': 0 / 60.0,
    'x5_appetizer.hit': 4,

    'x6_appetizer.dmg': 24 / 100.0,
    'x6_appetizer.sp': 0,
    'x6_appetizer.startup': 6 / 60.0,
    'x6_appetizer.recovery': 0 / 60.0,
    'x6_appetizer.hit': 4,

    'x7_appetizer.dmg': 24 / 100.0,
    'x7_appetizer.sp': 0,
    'x7_appetizer.startup': 6 / 60.0,
    'x7_appetizer.recovery': 0 / 60.0,
    'x7_appetizer.hit': 4,

    # C3 A B C D
    'x8_appetizer.dmg': 143 / 100.0,
    'x8_appetizer.sp': 1030,
    'x8_appetizer.startup': 46 / 60.0,
    'x8_appetizer.recovery': 0 / 60.0,
    'x8_appetizer.hit': 1,

    'x9_appetizer.dmg': 143 / 100.0,
    'x9_appetizer.sp': 0,
    'x9_appetizer.startup': 99 / 60.0,
    'x9_appetizer.recovery': 0 / 60.0,
    'x9_appetizer.hit': 1,

    'x1_appetizer0.dmg': 143 / 100.0,
    'x1_appetizer0.sp': 0,
    'x1_appetizer0.startup': 4 / 60.0,
    'x1_appetizer0.recovery': 0 / 60.0,
    'x1_appetizer0.hit': 1,

    'x1_appetizer1.dmg': 143 / 100.0,
    'x1_appetizer1.sp': 0,
    'x1_appetizer1.startup': 4 / 60.0,
    'x1_appetizer1.recovery': 9 / 60.0,
    'x1_appetizer1.hit': 1,
}


class Valerio(StanceAdv):
    conf = valerio_conf
    conf['slots.a'] = The_Wyrmclan_Duo()+Primal_Crisis()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Siren()
    conf['acl'] = """
        `s3, not buff(s3) 
        `s2(entree), self.inspiration()=0
        `s2(dessert)
        `s4
        `s1(appetizer), buff(s1, appetizer, timeleft) < 7
        `s1(dessert)
    """
    conf['coabs'] = ['Summer_Estelle', 'Renee', 'Xander']
    conf['afflict_res.frostbite'] = 0
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

    def prerun(self):
        random.seed()
        self.config_stances({
            'appetizer': ModeManager('appetizer', x=True, s1=True, s2=True),
            'entree': ModeManager('entree', x=True, s1=True, s2=True),
            'dessert': ModeManager('dessert', x=True, s1=True, s2=True),
        }, hit_threshold=20)
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