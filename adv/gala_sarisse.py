from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Gala_Sarisse

class Gala_Sarisse(Adv):
    a3 = ('bt',0.3)
    conf = {}
    conf['slots.a'] = Forest_Bonds()+Primal_Crisis()
    conf['slots.d'] = Gala_Mars()
    conf['acl'] = """
        `dragon(c3-s-c3-c3-s-end), s=1
        `s3, not self.s3_buff
        `s1
        `s4, s=1
        `s2, cancel
        `fs, x=4
        """
    conf['coabs'] = ['Blade', 'Wand', 'Marth']
    conf['share'] = ['Summer_Cleo']

    def prerun(self):
        self.ahits = 0
        self.s2stance = 0

    def dmg_proc(self, name, amount):
        if self.condition('always connect hits'):
            if self.hits // 20 > self.ahits:
                self.ahits = self.hits // 20
                Selfbuff('sylvan strength',0.02,15).no_bufftime().on()
                Selfbuff('sylvan crit',0.01,15,'crit','chance').no_bufftime().on()

    def s1_proc(self, e):
        buffcount = min(self.buffcount, 7)
        self.dmg_make(e.name,0.95*buffcount)
        self.add_hits(buffcount)

    def s2_proc(self, e):
        if self.s2stance == 0:
            Teambuff(f'{e.name}_str',0.20,10).on()
            self.s2stance = 1
        elif self.s2stance == 1:
            Teambuff(f'{e.name}_def',0.20,15,'defense').on()
            self.s2stance = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
