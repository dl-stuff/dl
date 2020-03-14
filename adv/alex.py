from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Alex

class Alex(Adv):
    comment = 'not consider bk boost of her s2'
    a1 = ('s',0.35,'hp100')
    a3 = ('sp',0.05)

    conf = {}
    conf['slot.a'] = Twinfold_Bonds()+The_Plaguebringer()
    conf['slot.d'] = Fatalis()
    conf['acl'] = """
        `s3, not this.s3_buff
        `s1
        `s2
        `fs, x=4
        """
    conf['afflict_res.poison'] = 0

    def s1_proc(self, e):
        self.afflics.poison('s1',100,0.396)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)

