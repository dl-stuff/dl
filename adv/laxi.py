import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Laxi

class Laxi(Adv):
    comment = "a1 proc at 0s"
    
    conf = {}
    conf['slot.a'] = MF()+DD()
    conf['slot.d'] = Dreadking_Rathalos()
    conf['acl'] = """
        `dragon, fsc
        `s3, fsc and not this.s3_buff
        `s2, not this.s2buff.get()
        `s1
        `fs, x=2
        """

    def prerun(self):
        self.hp = 0.0
        
        self.healed = 0
        self.heal = Action('heal')
        self.heal.conf.startup = 0.1
        self.heal.conf.recovery = 5.0

        self.heal_initial = Timer(self.heal_proc,0).on()
        self.s2buff = Selfbuff("s2",0.15,-1)
        self.s2tick = Timer(self.s2_tick,2.9,1)

        self.a3buff = Selfbuff("a3",0.2,-1,"att","passive")

    def s1_proc(self, e):
        if self.s2buff.get() != 0:
            self.dmg_make("o_s1_boost",0.87*4)

    def s2_proc(self, e):
        # self.s2buff.on()
        if not self.s2buff.get():
            self.s2buff.on()
            self.s2tick.on()
        else:
            self.s2buff.off()
            self.s2tick.off()

    def s2_tick(self, t):
        if self.hp >= 4.0:
            self.hp -= 3.5
        if self.hp <= 30.0:
            self.a3buff.on()
            if self.healed == 0:
                self.heal_proc(None)
        else:
            self.a3buff.off()

    def heal_proc(self, t):
        self.healed = 1
        self.hp = 100.0
        self.s2buff.off()
        self.s2tick.off()
        self.a3buff.off()

        self.heal.getdoing().cancel_by.append('heal')
        self.heal.getdoing().interrupt_by.append('heal')
        self.heal()
if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

