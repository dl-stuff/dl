from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Euden

class Euden(Adv):
    a1 = ('dc', 4)
    
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+Me_and_My_Bestie()
    conf['slots.d'] = Gala_Mars()
    conf['acl'] = """
		`dragon.act('c3 s s end')
		`s3, not self.s3_buff
		`s1
		`s2, fsc
		`s4, fsc
		`fs, x=2
    """
    coab = ['Blade', 'Wand', 'Yuya']
    conf['afflict_res.burn'] = 0
    share = ['Kleimann']

    def s1_proc(self, e):
        self.afflics.burn(e.name,110,0.883)
        self.dragonform.charge_gauge(30)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)