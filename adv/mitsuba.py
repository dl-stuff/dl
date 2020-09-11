from core.advbase import *
from slot.a import *
from slot.d import *
from module.x_alt import X_alt
from module.template import StanceAdv

def module():
    return Mitsuba

mitsuba_conf = {
    # Mitsuba's Sashimi Combo
    # Total: 225
    # Total (Without Recovery): 202

    # C1: 11

    # C2A: 20
    # C2B: 20
    # C2C: 20

    # C3A: 23
    # C3B: 17
    # C3C: 25
    # C3D: 16
    # C3E: 34
    # C3F: 16
    # Recovery: 23

    # sC1 1x76%, 150SP
    # sC2 3x101%, 430SP
    # sC3 6x126%, 860SP

    # C1 A
    'x1_sashimi.dmg': 76 / 100.0,
    'x1_sashimi.sp': 150,
    'x1_sashimi.startup': 11 / 60.0,
    'x1_sashimi.recovery': 0 / 60.0,
    'x1_sashimi.hit': 1,

    # C2 A B C
    'x2_sashimi.dmg': 101 / 100,
    'x2_sashimi.sp': 430,
    'x2_sashimi.startup': 20 / 60.0,
    'x2_sashimi.recovery': 0 / 60.0,
    'x2_sashimi.hit': 1,

    'x3_sashimi.dmg': 101 / 100,
    'x3_sashimi.sp': 0,
    'x3_sashimi.startup': 20 / 60.0,
    'x3_sashimi.recovery': 0 / 60.0,
    'x3_sashimi.hit': 1,

    'x4_sashimi.dmg': 101 / 100,
    'x4_sashimi.sp': 0,
    'x4_sashimi.startup': 20 / 60.0,
    'x4_sashimi.recovery': 0 / 60.0,
    'x4_sashimi.hit': 1,

    # C3 A B C D E F
    'x5_sashimi.dmg': 126 / 100,
    'x5_sashimi.sp': 860,
    'x5_sashimi.startup': 23 / 60.0,
    'x5_sashimi.recovery': 0 / 60.0,
    'x5_sashimi.hit': 1,

    'x6_sashimi.dmg': 126 / 100,
    'x6_sashimi.sp': 0,
    'x6_sashimi.startup': 17 / 60.0,
    'x6_sashimi.recovery': 0 / 60.0,
    'x6_sashimi.hit': 1,

    'x7_sashimi.dmg': 126 / 100,
    'x7_sashimi.sp': 0,
    'x7_sashimi.startup': 25 / 60.0,
    'x7_sashimi.recovery': 0 / 60.0,
    'x7_sashimi.hit': 1,

    'x8_sashimi.dmg': 126 / 100,
    'x8_sashimi.sp': 0,
    'x8_sashimi.startup': 16 / 60.0,
    'x8_sashimi.recovery': 0 / 60.0,
    'x8_sashimi.hit': 1,

    'x9_sashimi.dmg': 126 / 100,
    'x9_sashimi.sp': 0,
    'x9_sashimi.startup': 34 / 60.0,
    'x9_sashimi.recovery': 0 / 60.0,
    'x9_sashimi.hit': 1,

    'x10_sashimi.dmg': 126 / 100,
    'x10_sashimi.sp': 0,
    'x10_sashimi.startup': 16 / 60.0,
    'x10_sashimi.recovery': 23 / 60.0,
    'x10_sashimi.hit': 1,

    # Mitsuba's Tempura Combo:
    # Total: 302
    # Total (Without Recovery): 241

    # C1: 11

    # C2A: 16
    # C2B: 32
    # C2C: 32
    # C2D: 35

    # C3A: 42
    # C3B: 26
    # C3C: 8
    # C3D: 6
    # C3E: 20
    # C3F: 6
    # C3G: 6
    # Recovery: 61

    # tC1 1x76%, 150SP
    # tC2 4x102%, 995SP
    # tC3 7x117%, 1220SP

    # C1 A
    'x1_tempura.dmg': 76 / 100.0,
    'x1_tempura.sp': 150,
    'x1_tempura.startup': 11 / 60.0,
    'x1_tempura.recovery': 0 / 60.0,
    'x1_tempura.hit': 1,

    # C2 A B C D
    'x2_tempura.dmg': 102 / 100,
    'x2_tempura.sp': 995,
    'x2_tempura.startup': 16 / 60.0,
    'x2_tempura.recovery': 0 / 60.0,
    'x2_tempura.hit': 1,

    'x3_tempura.dmg': 102 / 100,
    'x3_tempura.sp': 0,
    'x3_tempura.startup': 32 / 60.0,
    'x3_tempura.recovery': 0 / 60.0,
    'x3_tempura.hit': 1,

    'x4_tempura.dmg': 102 / 100,
    'x4_tempura.sp': 0,
    'x4_tempura.startup': 32 / 60.0,
    'x4_tempura.recovery': 0 / 60.0,
    'x4_tempura.hit': 1,

    'x5_tempura.dmg': 102 / 100,
    'x5_tempura.sp': 0,
    'x5_tempura.startup': 35 / 60.0,
    'x5_tempura.recovery': 0 / 60.0,
    'x5_tempura.hit': 1,

    # C3 A B C D E F
    'x6_tempura.dmg': 117 / 100,
    'x6_tempura.sp': 1220,
    'x6_tempura.startup': 42 / 60.0,
    'x6_tempura.recovery': 0 / 60.0,
    'x6_tempura.hit': 1,

    'x7_tempura.dmg': 117 / 100,
    'x7_tempura.sp': 0,
    'x7_tempura.startup': 26 / 60.0,
    'x7_tempura.recovery': 0 / 60.0,
    'x7_tempura.hit': 1,

    'x8_tempura.dmg': 117 / 100,
    'x8_tempura.sp': 0,
    'x8_tempura.startup': 8 / 60.0,
    'x8_tempura.recovery': 0 / 60.0,
    'x8_tempura.hit': 1,

    'x9_tempura.dmg': 117 / 100,
    'x9_tempura.sp': 0,
    'x9_tempura.startup': 6 / 60.0,
    'x9_tempura.recovery': 0 / 60.0,
    'x9_tempura.hit': 1,

    'x10_tempura.dmg': 117 / 100,
    'x10_tempura.sp': 0,
    'x10_tempura.startup': 20 / 60.0,
    'x10_tempura.recovery': 0 / 60.0,
    'x10_tempura.hit': 1,

    'x11_tempura.dmg': 117 / 100,
    'x11_tempura.sp': 0,
    'x11_tempura.startup': 6 / 60.0,
    'x11_tempura.recovery': 0 / 60.0,
    'x11_tempura.hit': 1,

    'x12_tempura.dmg': 117 / 100,
    'x12_tempura.sp': 0,
    'x12_tempura.startup': 6 / 60.0,
    'x12_tempura.recovery': 61 / 60.0,
    'x12_tempura.hit': 1,

    # Mitsuba's FS:
    # During stances, recovery goes from 14 to 34.
    # C2A FS Delay: 6
    # FSF Recovery: 22

    'fs.x2.charge': 14 / 60,
    'fs.recovery': 34 / 60,
    'fsf.startup': 14 / 60, # 22 - 8
}

class Mitsuba(StanceAdv):
    conf = mitsuba_conf.copy()
    conf['slots.a'] = Twinfold_Bonds()+His_Clever_Brother()
    conf['slots.d'] = Siren()
    # tc2afsf tc2a- s1
    conf['acl'] = """
        `tempura
        if x=2
        `s4
        `s3
        `s2
        `s1(sashimi), not self.afflics.frostbite.get()
        `s1, self.afflics.frostbite.get()
        `fsf
        end

        # buffbot mitsuba w/ G&C
        # `tempura
        # if x=2
        # `s2
        # `s4
        # `s3
        # `fsf
        # end
    """
    conf['coabs'] = ['Blade','Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Eugene']
    conf['afflict_res.frostbite'] = 0

    def prerun(self):
        self.config_stances({
            'sashimi': ModeManager('sashimi', x=True, s1=True, s2=True),
            'tempura': ModeManager('tempura', x=True, s1=True, s2=True)
        }, hit_threshold=20)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)