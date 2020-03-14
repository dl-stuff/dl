from core.advbase import *

def module():
    return Norwin

class Norwin(Adv):
    a3 = ('k_blind', 0.20)
    conf = {}
    conf['acl'] = """
        `dragon, fsc
        `s3, not this.s3_buff
        `s1
        `s2
        `fs, x=5
    """
    conf['afflict_res.blind'] = 80

    def s1_proc(self, e):
        r = self.afflics.blind('s1',100)
        if r > 0:
            Teambuff('a1',0.15*r,10).on()

    def s2_proc(self, e):
        with Modifier("s1killer", "blind_killer", "hit", 0.44):
            self.dmg_make('s1',3*2.45)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
