from core.advbase import *
from slot.a import *

def module():
    return Luca

class Luca(Adv):
    a1 = ('a',0.13,'hp100')

    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon
        `s3
        `s1, cancel
        `s4, cancel
        `s2, fsc
        `fs, x=5
        """
    conf['coabs'] = ['Cleo','Raemond','Peony']
    conf['share'] = ['Summer_Patia']
    conf['afflict_res.paralysis'] = 0

    def s1_proc(self, e):
        self.afflics.paralysis(e.name,110,0.883)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)