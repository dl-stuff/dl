import adv.adv_test
from core.advbase import *
from slot.a import *

def module():
    return Ryozen

class Ryozen(Adv):
    a3 = ('od',0.08)
    conf = {}
    conf['slots.a'] = RR()+The_Red_Impulse()
    conf['acl'] = """
        `dragon
        `s3
        `s4, cancel
        `s2, x=5
        `fs, x=5
        """
    conf['coabs'] = ['Cleo','Raemond','Peony']
    conf['share'] = ['Kleimann']
    
    def s1_proc(self, e):
        Teambuff(e.name, 0.25, 15, 'defense').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)