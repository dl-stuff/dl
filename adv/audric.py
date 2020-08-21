from core.advbase import *
from slot.a import *

def module():
    return Audric

class Audric(Adv):
    a1 = ('dp', 10)
    
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+Primal_Crisis()
    conf['acl'] = """
        `dragon.act('c3 s end'), fsc and (self.dragonform.shift_count<3 or (self.dragonform.shift_count<=3 and self.slots.tmp.d.trickery <= 1))
        `s3, not self.s3_buff
        `s1
        `s4, cancel
        `s2, fsc
        `fs, x=3
    """
    coab = ['Wand','Cleo','Forte']
    share = ['Curran']

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
        self.dragonform.charge_gauge(30)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
