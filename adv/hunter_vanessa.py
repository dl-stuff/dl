from core.advbase import *

def module():
    return Hunter_Vanessa


class Hunter_Vanessa(Adv):
    conf = {}
    conf['slots.a'] = ['Mega_Friends', 'Spirit_of_the_Season']
    conf['acl'] = """
        `dragon, s
        `s2, not buff(s2)
        `fs2, (s1.charged>=s1.sp-self.sp_val(fs2) or s4.charged>=s4.sp-self.sp_val(fs2))
        `s3, not buff(s3) and fsc
        `s1, fsc
        `s4, fsc
        `dodge,fsc
        `fs2, x=5
        """
    conf['coabs'] = ['Sharena','Blade','Peony']
    conf['afflict_res.paralysis'] = 0
    conf['share'] = ['Kleimann']

    def d_slots(self):
        if self.duration <= 60:
            self.conf['slots.a'] = ['Mega_Friends', 'The_Chocolatiers']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
