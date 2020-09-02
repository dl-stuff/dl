from core.advbase import *
from slot.a import *

def module():
    return Summer_Luca

class Summer_Luca(Adv):
    a1 = ('a',0.1,'hp70')
    a3 = ('eextra', 0.4)

    conf = {}
    conf['slots.a'] = RR()+The_Red_Impulse()
    conf['acl'] = """
        `dragon
        `s1
        `s3
        `s4, x=4
        `s2, cancel
        """
    conf['coabs'] = ['Raemond','Lucretia','Peony']
    conf['share'] = ['Ranzal']
    
    def d_coabs(self):
        if self.sim_afflict:
            self.conf['coabs'] = ['Raemond','Cleo','Peony']

    def s2_proc(self, e):
        Spdbuff(e.name,0.2,10).on()
        self.energy.add(1)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
