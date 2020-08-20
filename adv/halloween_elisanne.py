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
    conf['slots.paralysis.a'] = conf['slots.a']
    conf['acl'] = """
        `dragon.act('c3 s end'), x=5 or s
        `s2, s1.charged<=s1.sp-700 and s4.charged<=s4.sp-700 
        `s4, self.afflics.poison.get() or x=5
        `s3
        `s1
        `fs, x=5
        """
    coab = ['Wand','Sharena','Peony']
    conf['afflict_res.paralysis'] = 0
    share = ['Ranzal','Curran']

    def prerun(self):
        self.phase['s1'] = 0
        self.vampire_maiden = vampire_maiden(self, 'vampire_maiden',1, 15,'ss','ss')
        self.vampire_maiden_xalt = X_alt(self, 'vampire_maiden_xalt', vm_auto_conf, x_proc=self.l_vm_x)

    def l_vm_x(self, e):
        self.vampire_maiden_xalt.x_proc_default(e)
    
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
        self.vampire_maiden.on()
        self.vampire_maiden_xalt.on()

class vampire_maiden(Selfbuff):
    def __init__(self, adv, name='<buff_noname>', value=0, duration=0, mtype=None, morder=None):
        Buff.__init__(self, name, value, duration, mtype, morder)
        self.adv = adv
        self.bufftype = 'self' 

    def buff_end_proc(self, e):
        Buff.buff_end_proc(self, e)
        self.adv.vampire_maiden_xalt.off()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
