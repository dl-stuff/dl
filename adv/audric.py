from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Audric

class Audric(Adv):
    a1 = ('dp', 10)
    
    conf = {}
    conf['slot.a'] = The_Shining_Overlord()+The_Fires_of_Hate()
    conf['slot.d'] = Epimetheus()
    conf['acl'] = """
        `dragon
        `s3, fsc and not this.s3_buff
        `s1, fsc
        `s2, fsc
        `fs, x=3
    """
    def prerun(self):
        self.cursed_blood = Selfbuff('cursed_blood',0.30,-1,'crit','chance')
        Event('dragon').listener(self.a3_on)
        Event('idle').listener(self.a3_off)

    def a3_on(self, e):
        if not self.cursed_blood.get():
            self.cursed_blood.on()

    def a3_off(self, e):
        if self.cursed_blood.get():
            self.cursed_blood.off()

    def s1_proc(self, e):
        self.dragonform.charge_gauge(3)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
