from core.advbase import *
from slot.a import *

def module():
    return Amane

class Amane(Adv):
    a1 = [('prep',1.00), ('scharge_all', 0.05)]
    a3 = ('bk',0.35)
    
    conf = {}
    conf['slots.a'] = CC()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon, cancel
        queue prep
        `s2;s3;s1;s4
        end
        `s1
        `s4, x>3
        `s3, cancel
        `s2, x>3
        """
    coab = ['Blade','Sharena','Peony']
    share = ['Summer_Patia']

    def s1_proc(self, e):
        with KillerModifier('s1_killer', 'hit', 0.1, ['paralysis']):
            self.dmg_make(e.name, 4.92)
            self.afflics.paralysis(e.name,120,0.97)
            self.dmg_make(e.name, 4.92)
            
            for _ in range(min(self.buffcount, 2)):
                self.dmg_make(e.name, 0.35)
                self.add_hits(1)

    def s2_proc(self, e):
        self.buff_max_hp(f'{e.name}_hp', 0.15)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
