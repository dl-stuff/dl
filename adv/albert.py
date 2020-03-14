import adv.adv_test
from core.advbase import *
import copy
from module.x_alt import Fs_alt
from slot.a import *
from slot.d import *

def module():
    return Albert


class Albert(Adv):
    a1 = ('fs',0.5)
    conf = {}
    conf['acl'] = """
        `s2, s1.charged>=s1.sp-330
        `fs, s=2 and not self.afflics.paralysis.get()
        `s1, fsc
        `s3, fsc
        `fs, seq=2
        """
    conf['slot.a'] = TSO()+SDO()
    conf['slot.d'] = C_Phoenix()
    conf['afflict_res.paralysis'] = 0

    def init(self):
        if self.condition('big hitbox'):
            self.s1_proc = self.c_s1_proc

    def fs_proc_alt(self, e):
        self.afflics.paralysis('fs',100,0.803)

    def prerun(self):
        conf_fs_alt = {
            'fs.dmg':1.02,
            'fs.sp':330,
            'fs.recovery':26/60.0,
        }
        self.fs_alt = Fs_alt(self, Conf(conf_fs_alt), self.fs_proc_alt)
        self.s2.autocharge_init(self.s2autocharge).on()
        self.s2buff = Selfbuff("s2_shapshift",1, 20,'ss','ss')
        self.a3 = Selfbuff('a2_str_passive',0.25,20,'att','passive')

        self.fs_alt_timer = Timer(self.fs_alt_end)

    def fs_alt_end(self,t):
        self.fs_alt.off()

    def s2autocharge(self, t):
        if not self.s2buff.get():
            self.s2.charge(160000.0/40)
            log('sp','s2autocharge')

    def c_s1_proc(self, e):
        if self.s2buff.get():
            self.dmg_make("o_s1_s2boost",12.38-0.825)
            self.dmg_make("o_s1_hit2", 0.83)
            self.dmg_make("o_s1_hit3", 0.83)
            self.dmg_make("o_s1_hit4", 0.83)
            self.dmg_make("o_s1_hit5", 0.83)
            self.dmg_make("o_s1_hit6", 0.83)
            self.s2buff.buff_end_timer.timing += 2.6
            self.a3.buff_end_timer.timing += 2.6


    def s1_proc(self, e):
        if self.s2buff.get():
            self.dmg_make("o_s1_s2boost",12.38-0.825)
            self.dmg_make("o_s1_hit2", 0.83)
            self.dmg_make("o_s1_hit3", 0.83)
            self.dmg_make("o_s1_hit4", 0.83)
            self.s2buff.buff_end_timer.timing += 2.6
            self.a3.buff_end_timer.timing += 2.6

    def s2_proc(self, e):
        self.s2buff.on()
        self.a3.on()
        self.fs_alt.on(-1)
        self.fs_alt_timer(20)


if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

