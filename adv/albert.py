from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Albert

albert_fs = {
    'fs': {'dmg': 1.265},
    'fs1': {
        'dmg': 1.12,
        'sp': 330,
        'charge': 4 / 60.0,
        'startup': 9 / 60.0,
        'recovery':26 / 60.0,
        'hit': 1,
    },
    'fs2': {
        'dmg': 1.12,
        'sp': 330,
        'charge': 34 / 60.0, # 0.5 ?
        'startup': 9 / 60.0,
        'recovery':26 / 60.0,
        'hit': 1,
    }
}

class Albert(Adv):
    conf = albert_fs.copy()
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
    conf['coabs'] = ['Blade','Lucretia','Peony']
    conf['share'] = ['Summer_Patia']
    conf['afflict_res.paralysis'] = 0

    def init(self):
        self.conf.fs.hit = 1

    def prerun(self):
        self.s2.autocharge_init(self.s2autocharge).on()
        self.a1_fs = Selfbuff('a1_fs_passive',0.10, 25,'fs','passive')
        self.a3_att = Selfbuff('a3_att_passive',0.30, 25,'att','passive')
        self.a3_spd = Spdbuff('a3_spd', 0.10, 25)
        self.fs_alt = FSAltBuff(self, duration=25)
        self.electrified = MultiBuffManager([self.a1_fs, self.a3_att, self.a3_spd], duration=25)

        self.s1_hits = 6 if self.condition('big hitbox') else 4

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.electrified = Dummy()

    def s2autocharge(self, t):
        if not self.electrified.get():
            self.s2.charge(4480)

    def fs_proc(self, e):
        if not self.electrified.get():
            self.s2.charge(-8000)
        elif e.name == 'fs2':
            self.afflics.paralysis('fs',120,0.97)

    def s1_proc(self, e):
        with KillerModifier('s1_killer','hit',0.2,['paralysis']):
            if self.electrified.get():
                self.dmg_make(e.name, 12.38)
                for _ in range(2, self.s1_hits+1):
                    self.dmg_make(e.name, 0.83)
                    self.add_hits(1)
                self.electrified.add_time(self.s1.ac.getstartup()+self.s1.ac.getrecovery())
            else:
                self.dmg_make(e.name, 8.25)

    def s2_proc(self, e):
        self.electrified.on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)