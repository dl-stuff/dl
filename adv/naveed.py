from core.advbase import *

def module():
    return Naveed

class Naveed(Adv):
    conf = {}
    conf['acl'] = """
        `dragon,s
        `s3, not buff(s3)
        `s2, naveed_bauble < 5
        `s1, cancel
        `s4, fsc
        `fs, x=3 and cancel
        """
    conf['slots.a'] = ['The_Shining_Overlord', 'Primal_Crisis']
    conf['coabs'] = ['Blade', 'Wand', 'Marth']
    conf['share'] = ['Summer_Patia']

    def prerun(self):
        self.naveed_bauble = 0

    def s2_proc(self, e):
        if self.naveed_bauble < 5:
            self.naveed_bauble += 1

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
