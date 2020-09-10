from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Wu_Kong

class Wu_Kong(Adv):
    a3 = ('k_paralysis',0.3)

    conf = {}
    conf['slots.a'] = Twinfold_Bonds()+The_Fires_of_Hate()
    conf['slots.paralysis.a'] = Twinfold_Bonds()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon, s
        `s3, not self.s3_buff
        `s4
        `s2
        `s1
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Lucretia','Peony']
    conf['share'] = ['Kleimann']

    def prerun(self):
        self.phase['s1'] = 0

    def s1_proc(self, e):
        self.phase[e.name] += 1
        if self.phase[e.name] == 1:
            self.dmg_make(e.name, 5.46)
        elif self.phase[e.name] == 2:
            self.dmg_make(e.name, 5.73)
        elif self.phase[e.name] == 3:
            self.dmg_make(e.name, 6.00)
        self.phase[e.name] %= 3

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)