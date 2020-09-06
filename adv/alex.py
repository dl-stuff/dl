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
    conf['slots.a'] = Twinfold_Bonds()+The_Fires_of_Hate()
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = """
        `dragon(c3-s-end), self.trickery <= 1
        `s3, not self.s3_buff
        `s4
        `s2
        `s1, cancel
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Wand','Bow']
    conf['afflict_res.poison'] = 0
    conf['share'] = ['Curran']

    def s1_proc(self, e):
        self.afflics.poison(e.name,100,0.396)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)