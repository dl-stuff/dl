from core.advbase import *

def module():
    return Amane

class Amane(Adv):
    a3 = ('bk',0.2)
    a1 = ('prep',0.75)
    
    conf = {}
    conf['acl'] = """
        `dragon
        `s2
        `s1
        `s3, x=5
        `s4, x=5
        """
    coab = ['Blade','Halloween_Elisanne','Peony']
    share = ['Ranzal']

    def s1_proc(self, e):
        with KillerModifier('s1_killer', 'hit', 0.1, ['paralysis']):
            self.dmg_make(e.name, 4.92)
            self.afflics.paralysis(e.name,120,0.97)
            self.dmg_make(e.name, 4.92)
            
            for _ in range(min(self.buffcount, 2)):
                self.dmg_make(f'o_{e.name}_boost',0.35)
                self.add_hits(1)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
