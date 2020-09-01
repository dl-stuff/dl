from core.advbase import *
from slot.a import *

def module():
    return Alfonse

class Alfonse(Adv):
    a1 = [('lo',0.40, 10.0),('lo',0.10,-1)]
    a3 = ('sp',0.10)

    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon
        `s3, cancel
        `s2, cancel
        `s4, cancel
        `s1, fsc or not self.afflics.paralysis.get()
        `fs, x=2
    """
    coab = ['Sharena','Lucretia','Peony']
    share = ['Kleimann']	

    def s1_before(self, e):
        Selfbuff('s1_buff',0.20,12).on()

    def s1_proc(self, e):
        self.afflics.paralysis(e.name,120, 0.97)

    def s2_proc(self, e):
        with CrisisModifier(e.name, 1.00, self.hp):
            self.dmg_make(e.name, 7.32)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)