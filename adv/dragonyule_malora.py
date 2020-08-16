from core.advbase import *
from slot.a import *

def module():
    return Dragonyule_Malora

class Dragonyule_Malora(Adv):
    a1 = ('od',0.13)

    conf = {}
    conf['slots.a'] = Summer_Paladyns() + Primal_Crisis()
    conf['slots.paralysis.a'] = Summer_Paladyns() + Spirit_of_the_Season()
    conf['acl'] = """
		`dragon.act("c3 s end")
		`s1
		`s2, self.def_mod()!=1
		`s4, cancel
		`s3, x=4
        """
    coab = ['Wand','Dagger','Peony']
    share = ['Ranzal','Kleimann']

    def prerun(self):
        self.s1debuff = Debuff('s1',0.15,15) if self.condition('buff all team') else None

    def s1_proc(self, e):
        if self.s1debuff is not None:
            self.s1debuff.on()
        self.dmg_make(e.name,4.67,'s')
        self.add_hits(1)

    def s2_proc(self, e):
        with KillerModifier('s2_killer', 'hit', 0.8, ['debuff_def']):
            self.dmg_make(e.name, 12.96)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)