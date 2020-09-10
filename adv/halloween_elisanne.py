from core.advbase import *
from slot.a import *
from module.x_alt import X_alt
import wep.lance

def module():
    return Halloween_Elisanne

vm_auto_conf = wep.lance.conf.copy()
vm_auto_conf.update({
    'x1.dmg': 0.6006,
    'x2.dmg': 0.32175,
    'x3.dmg': 0.7722,
    'x4.dmg': 1.0725,
    'x5.dmg': 0.8008,

    'x1.sp': 180,
    'x2.sp': 360,
    'x3.sp': 180,
    'x4.sp': 720,
    'x5.sp': 900,
})

class Halloween_Elisanne(Adv):
    a1 = ('s',0.35)

    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon
        `s3, not self.s3_buff
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
        self.vampire_maiden = X_alt(self, 'vampire_maiden', vm_auto_conf)
        self.vampire_maiden_buff = EffectBuff(
            'vampire_maiden', 15, 
            lambda: self.vampire_maiden.on(), 
            lambda: self.vampire_maiden.off()
        )

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.rebind_function(Halloween_Elisanne, 's1_latency')
        adv.phase[dst] = 0

    def s1_latency(self, t):
        Teambuff(t.name,0.13,15).on()

    def s1_proc(self, e):
        self.phase[e.name] += 1
        with KillerModifier(e.name, 'hit', 0.2 * int(self.phase[e.name] == 3), ['paralysis']):
            self.dmg_make(e.name, 1.17)
            if self.phase[e.name] > 1:
                t = Timer(self.s1_latency)
                t.name = e.name
                t.on(2.5)
                self.afflics.paralysis(e.name, 120, 0.97)
            self.dmg_make(e.name, 1.17*6)
        self.phase[e.name] %= 3
        
    def s2_proc(self, e):
        self.charge(e.name, 700)
        self.vampire_maiden_buff.on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
