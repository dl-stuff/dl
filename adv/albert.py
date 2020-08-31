from core.advbase import *
from module.x_alt import Fs_alt
from slot.a import *
from slot.d import *

def module():
    return Albert

conf_alt_fs = {
    'fs1': {
        'dmg': 1.12,
        'sp': 330,
        'charge': 4 / 60.0,
        'startup': 9 / 60.0,
        'recovery':26 / 60.0,
    },
    'fs2': {
        'dmg': 1.12,
        'sp': 330,
        'charge': 34 / 60.0, # 0.5 ?
        'startup': 9 / 60.0,
        'recovery':26 / 60.0,
    }
}

# non electrified fs
conf_albert_fs = {
    'fs.dmg': 1.265
}

class Albert(Adv):
    a1 = ('fs',0.5)
    conf = conf_albert_fs.copy()
    conf['slots.a'] = The_Shining_Overlord()+Spirit_of_the_Season()
    conf['acl'] = """
        if self.electrified.get()
        `s1
        `s3, fsc
        if x=3
        `fs2, not self.afflics.paralysis.get()
        `fs1
        end
        else
        `dragon, cancel
        `s2, s1.charged>=s1.sp-self.sp_val(2)
        `s1, cancel
        `s3, cancel
        `s4, cancel
        end
        """
    coab = ['Blade','Lucretia','Peony']
    share = ['Summer_Patia']
    conf['afflict_res.paralysis'] = 0

    def init(self):
        self.conf.fs.hit = 1

    def prerun(self):
        self.s2.autocharge_init(self.s2autocharge).on()
        self.fs_alt = Fs_alt(self, conf_alt_fs, fs_proc=self.fs_proc)
        self.a1_fs = Selfbuff('a1_fs_passive',0.10, 25,'fs','passive')
        self.a3_att = Selfbuff('a3_att_passive',0.30, 25,'att','passive')
        self.a3_spd = Spdbuff('a3_spd', 0.10, 25)
        self.electrified = EffectBuff('electrified', 25, self.electrified_on, self.electrified_off)

        self.s1_hits = 6 if self.condition('big hitbox') else 4

    def electrified_on(self):
        self.fs_alt.on(-1)
        self.a1_fs.on()
        self.a3_att.on()
        self.a3_spd.on()

    def electrified_off(self):
        self.fs_alt.off()
        self.a1_fs.off()
        self.a3_att.off()
        self.a3_spd.off()

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.electrified = Dummy()

    def s2autocharge(self, t):
        if not self.electrified.get():
            self.s2.charge(28000)
            log('sp','s2autocharge')

    def fs_proc(self, e):
        if not self.electrified.get():
            self.s2.charge(-50000)
        elif e.name == 'fs2':
            self.afflics.paralysis('fs',120,0.97)

    def s1_proc(self, e):
        with KillerModifier('s1_killer','hit',0.2,['paralysis']):
            if self.electrified.get():
                self.dmg_make(e.name, 12.38)
                for _ in range(2, self.s1_hits+1):
                    self.dmg_make(e.name, 0.83)
                    self.add_hits(1)
                extend = self.s1.ac.getstartup()+self.s1.ac.getrecovery()
                for buff in (self.electrified,
                             self.a1_fs,
                             self.a3_att,
                             self.a3_spd):
                    buff.buff_end_timer.timing += extend
            else:
                self.dmg_make(e.name, 8.25)

    def s2_proc(self, e):
        self.electrified.on()
        self.a1_fs.on()
        self.a3_att.on()
        self.a3_spd.on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)