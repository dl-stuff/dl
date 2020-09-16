from core.advbase import *
from core.log import *
from slot.a import *
from slot.d import *

def module():
    return Serena

class Serena(Adv):
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+Primal_Crisis()
    conf['acl'] = """
        `dragon,s
        `s3, not buff(s3)
        `s4, fsc
        `s1, fsc
        `s2, fsc
        `fs, seq=3
        """
    conf['coabs'] = ['Blade', 'Yuya', 'Halloween_Mym']
    conf['share'] = ['Kleimann']

    def prerun(self):
        self.a1_count = 0
        self.a3_count = 0

    def add_combo(self):
        super().add_combo()
        if self.a1_count < 3 and self.a1_count != self.hits // 20:
            self.a1_count = self.hits // 20
            Selfbuff('a1_cd',0.06,-1,'crit','damage').on()
        if self.a3_count < 3 and self.a3_count != self.hits // 30:
            self.a3_count = self.hits // 30
            Selfbuff('a3_cc',0.03,-1,'crit','chance').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
