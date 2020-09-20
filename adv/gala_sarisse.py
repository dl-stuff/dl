from core.advbase import *

def module():
    return Gala_Sarisse

class Gala_Sarisse(Adv):
    conf = {}
    conf['slots.a'] = ['Forest_Bonds', 'Primal_Crisis']
    conf['slots.d'] = 'Gala_Mars'
    conf['acl'] = """
        `dragon(c3-s-c3-c3-s-end), s=1
        `s3, not buff(s3)
        `s1
        `s4, s=1
        `s2, cancel
        `fs, x=3
        """
    conf['coabs'] = ['Nobunaga', 'Wand', 'Marth']
    conf['share'] = ['Summer_Cleo']

    def prerun(self):
        self.ahits = 0
        self.s2stance = 0

    def add_combo(self, name='#'):
        super().add_combo(name)
        if self.condition('always connect hits'):
            if self.hits // 20 > self.ahits:
                self.ahits = self.hits // 20
                if name[0] == 's' or name == 'ds':
                    Selfbuff('sylvan strength',0.02,15).on()
                    Selfbuff('sylvan crit',0.01,15,'crit','chance').on()
                else:
                    Selfbuff('sylvan strength',0.02,15).ex_bufftime().on()
                    Selfbuff('sylvan crit',0.01,15,'crit','chance').ex_bufftime().on()

    # def s1_proc(self, e):
    #     buffcount = min(self.buffcount, 7)
    #     self.dmg_make(e.name,0.95*buffcount)
    #     self.add_hits(buffcount)

    # def s2_proc(self, e):
    #     if self.s2stance == 0:
    #         Teambuff(f'{e.name}_str',0.20,10).on()
    #         self.s2stance = 1
    #     elif self.s2stance == 1:
    #         Teambuff(f'{e.name}_def',0.20,15,'defense').on()
    #         self.s2stance = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
