from core.advbase import *
from slot.a import *

def module():
    return Luca

class Luca(Adv):

    conf = {}
    conf['slots.a'] = Forest_Bonds()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon, x=5
        `s3, not self.s3_buff and x=5
        `s2
        `s1
        `s4, cancel
        `fs, x=5
        """
    conf['coabs'] = ['Sharena','Lucretia','Peony']
    conf['share'] = ['Summer_Patia']
    conf['afflict_res.paralysis'] = 0

    def s1_proc(self, e):
        self.afflics.paralysis(e.name,120,0.97)
        
    def s2_proc(self,e):
        with KillerModifier('s2_killer','hit',0.3,['paralysis']):
            self.dmg_make(e.name,11.73)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)