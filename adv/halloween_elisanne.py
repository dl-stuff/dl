from core.advbase import *
from slot.a import *
from module.x_alt import X_alt
import wep.lance

def module():
    return Halloween_Elisanne

heli_copter ={
    'x1_vamp.dmg': 0.6006,
    'x2_vamp.dmg': 0.32175,
    'x3_vamp.dmg': 0.7722,
    'x4_vamp.dmg': 1.0725,
    'x5_vamp.dmg': 0.8008,

    'x1_vamp.sp': 180,
    'x2_vamp.sp': 360,
    'x3_vamp.sp': 180,
    'x4_vamp.sp': 720,
    'x5_vamp.sp': 900,
}

class Halloween_Elisanne(Adv):
    conf = heli_copter
    conf['slots.a'] = Resounding_Rendition()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon
        `s3, not buff(s3)
        `s2, s1.charged<=s1.sp-700 and s4.charged<=s4.sp-700 
        `s4
        `s1, cancel
        `fs, x=5
        """
    conf['coabs'] = ['Lucretia','Sharena','Peony']
    conf['afflict_res.paralysis'] = 0
    conf['share'] = ['Kleimann']

    def prerun(self):
        self.phase['s1'] = 0
        self.vampire_maiden = XAltBuff('vamp', duration=15, hidden=False)

    def s2_proc(self, e):
        self.charge(e.name, 700)
        self.vampire_maiden.on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
