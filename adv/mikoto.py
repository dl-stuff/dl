import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Mikoto

class Mikoto(Adv):
    a1 = ('cc',0.10,'hp70')
    a3 = ('cc',0.08)
    
    conf = {}
    conf['slot.a'] = RR() + BN()
    conf['slot.d'] = Arctos()
    conf['acl'] = """
        `s3, not self.s3_buff
        `s1, x = 5
        `s2, x = 5
        """

    def prerun(self):
        self.s1buff = Selfbuff("s1",0.0, 20)
        self.s2buff = Spdbuff("s2",0.2, 10)
        self.conf.s1.recovery = 1.4


    def s1latency(self, e):
        self.s1buff.off()
        self.s1buff.on()


    def s1_proc(self, e):
        buff = self.s1buff.get()
        if buff == 0:
            stance = 0
        elif buff == 0.10:
            stance = 1
        elif buff == 0.15:
            stance = 2
        if stance == 0:
            self.dmg_make('s1',5.32*2)
            self.s1buff.set(0.10,20) #.on()
            self.conf.s1.recovery = 1.4
            Timer(self.s1latency).on(1.5/self.speed())
        elif stance == 1:
            self.dmg_make('s1',3.54*3)
            self.s1buff.off()
            self.s1buff.set(0.15,15) #.on()
            self.conf.s1.recovery = 1.63
            Timer(self.s1latency).on(1.5/self.speed())
        elif stance == 2:
            self.dmg_make('s1',2.13*3+4.25)
            self.s1buff.off().set(0)
            self.conf.s1.recovery = 3.07

    def s2_proc(self, e):
        self.s2buff.on()


if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

