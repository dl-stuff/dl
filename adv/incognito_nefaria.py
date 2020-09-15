from core.advbase import *
from slot.a import *
from slot.d import *
from module.template import RngCritAdv

def module():
    return Incognito_Nefaria

class Incognito_Nefaria(RngCritAdv):
    comment = 'no s2. overall dps is only slightly lower without s2'
    conf = {}
    conf['slots.a'] = Candy_Couriers()+Levins_Champion()
    conf['acl'] = """
        # `dragon(c3-s-s-end), s and not self.energy()=5
        # `s3, not buff(s3) and x=5
        # `s1
        # `s4, x>2
        
        # S2 mode
        `dragon(c3-s-s-end), (s=1 and self.energy()=3) or s=2
        `s3, not buff(s3) and x=5
        `s2, self.energy()=5
        `s1, not self.energy()=5
        `s4, not self.energy()=5 and x>2
        """
    conf['slots.d'] = Gala_Mars()
    conf['coabs'] = ['Blade', 'Serena', 'Yuya']
    conf['share'] = ['Kleimann']
    conf['afflict_res.burn'] = 0

    def prerun(self):
        self.config_rngcrit(cd=7, ev=20)
        self.a1_buff = Selfbuff('a1', 0, 20, 'crit', 'damage')
        self.a1_stack = 0

    def rngcrit_cb(self, mrate=None):
        self.a1_buff.set(0.20*mrate)
        self.a1_buff.on()
        self.a1_stack = mrate - 1

    @property
    def buffcount(self):
        buffcount = super().buffcount
        return buffcount + self.a1_stack

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
