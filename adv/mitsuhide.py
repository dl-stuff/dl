from core.advbase import *
from slot.a import *

def module():
    return Mitsuhide

class Mitsuhide(Adv):
    conf = {}
    conf['slots.a'] = Twinfold_Bonds()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon, s=1
        `s3, not buff(s3) and x=4
        `s1
        `s2
        `s4, x>3 or fsc
        `fs, x=5
    """
    conf['coabs'] = ['Lucretia','Sharena','Peony']
    conf['share'] = ['Summer_Patia']
    conf['afflict_res.paralysis'] = 0

    def s2_before(self, e):
        # 5: 5
        # 10: 10
        # 15: 15 + 5
        # 20: 20 + 10
        # 25: 25 + 15
        # 30: 30 + 20
        mod = 0
        for i in range(1, 7):
            if self.hits >= i*5:
                mod += 5
        for i in range(3, 7):
            if self.hits >= i*5:
                mod += 5
        mod /= 100
        self.s2_combo_mod = Modifier('s2_combo_mod', 'att', 'skill_combo', mod).on()

    def s2_proc(self, e):
        self.s2_combo_mod.off()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
