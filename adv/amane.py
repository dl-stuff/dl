from core.advbase import *

def module():
    return Amane

class Amane(Adv):
    a1 = [('prep',1.00), ('scharge_all', 0.05)]
    a3 = ('bk',0.35)
    
    conf = {}
    conf['acl'] = """
        `dragon
        `s2
        `s1
        `s3
        `s4
        """
    coab = ['Blade','Sharena','Peony']
    share = ['Ranzal','Kleimann']

    def s1_proc(self, e):
        with KillerModifier('s1_killer', 'hit', 0.1, ['paralysis']):
            self.dmg_make(e.name, 4.92)
            self.afflics.paralysis(e.name,120,0.97)
            self.dmg_make(e.name, 4.92)
            
            for _ in range(min(self.buffcount, 2)):
                self.dmg_make(e.name, 0.35)
                self.add_hits(1)

    def s2_proc(self, e):
        if self.mod('maxhp') < 1.30:
            Selfbuff('s2_hp', 0.15, -1, 'maxhp', 'buff').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
