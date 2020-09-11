from core.advbase import *
from slot.a import *

def module():
    return Audric

class Audric(Adv):    
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end), fsc and ((self.dragonform.shift_count<3) or ((self.dragonform.shift_count<=3) and self.trickery <= 1))
        `s3, not buff(s3)
        `s1
        `s4, cancel
        `s2, fsc
        `fs, x=3
    """
    conf['coabs'] = ['Wand','Cleo','Forte']
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Curran']

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


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
