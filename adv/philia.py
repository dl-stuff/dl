from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Philia

class Philia(Adv):
    a1 = ('a',0.1,'hp100')
    conf = {}
    conf['slots.a'] = Forest_Bonds()+Primal_Crisis()
    conf['slots.poison.a'] = Resounding_Rendition()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon.act("c3 s end"), s4.check()
        `s3, not self.s3_buff
        `s4
        `s2
        `s1, cancel
        """
    coab = ['Blade','Dragonyule_Xainfried','Lin_You']
    share = ['Curran']
    conf['afflict_res.paralysis'] = 0

    def s2_proc(self, e):
        self.afflics.paralysis(e.name,90,0.60)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)