import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Rena

class Rena(Adv):
    a1 = ('primed_defense',0.08)

    conf = {}
    conf['slot.d'] = Sakuya()
    conf['slot.a'] = RR()+Elegant_Escort()
    conf['acl'] = """
        `dragon.act('c3 s end'), s=2
        `s3, not this.s3_buff_on
        `s1
        `s2, s=1
        `fs, seq=5 and (s1.charged=1500 or s1.charged=3200)
        """
    conf['afflict_res.burn'] = 0

    def prerun(self):
        self.stance = 0

    def s1_proc(self, e):
        if self.stance == 0:
            self.stance = 1
            self.dmg_make("s1", 0.72)
            self.hits += 1
            self.afflics.burn('s1',120,0.97)
            self.dmg_make("s1", 8.81)
            self.hits += 4

        elif self.stance == 1:
            self.stance = 2
            self.dmg_make("s1", 0.72)
            self.afflics.burn('s1',120,0.97)
            self.hits += 1
            self.dmg_make("s1", 8.81)
            Selfbuff('s1crit',0.1,15,'crit','chance').on()
            self.hits += 4

        elif self.stance == 2:
            self.stance = 0
            with Modifier("s1killer", "burn_killer", "hit", 0.8):
                self.dmg_make("s1", 0.72)
                self.hits += 1
                self.afflics.burn('s1',120,0.97)
                self.dmg_make("s1", 8.81)
                self.hits += 4
            Selfbuff('s1crit',0.1,15,'crit','chance').on()


    def s2_proc(self, e):
        self.s1.charge(self.s1.sp)

if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)
    #logcat(['cd'])
