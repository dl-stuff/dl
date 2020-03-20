import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Ramona

class Ramona(Adv):
    comment = ''
    a1 = ('primed_att',0.10)
    a3 = ('bc',0.13)
    
    conf = {}
    conf['slots.a'] = KFM() + VC()
    conf['slots.d'] = Sakuya()
    conf['acl'] = """
        `s3, not self.s3_buff
        `s1a
        `s2, x = 4
        """

    def prerun(self):
        self.a_s1 = self.s1.ac
        self.a_s1a = S('s1', Conf({'startup': 0.10, 'recovery': 3.10}))
        def recovery():
            return self.a_s1a._recovery + self.a_s1.getrecovery()
        self.a_s1a.getrecovery = recovery

    def s1back(self, t):
        self.s1.ac = self.a_s1

    def s1a(self):
        if self.s1.check():
            self.dmg_make('s1', 2.93*6)
            self.hits += 6
            self.s1.ac = self.a_s1a
            Timer(self.s1back).on(self.conf.s1.startup+0.01)
            return self.s1()
        else:
            return 0

    def s2_proc(self, e):
       Event('defchain')()



if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)

