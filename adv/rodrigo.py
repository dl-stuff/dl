from core.advbase import *
from slot.a import *

def module():
    return Rodrigo

class Rodrigo(Adv):
    a1 = ('a',0.15,'hp70')
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end),fsc
        `s3, fsc and not self.s3_buff
        `s4
        `s1, cancel and self.s3_buff
        `s2, fsc
        `fs, x=2 and s1.charged > 841
        `fs, x=3
        """
    conf['coabs'] = ['Ieyasu','Wand','Forte']
    conf['share'] = ['Curran']

    def s1_proc(self, e):
        self.afflics.poison(e.name,120,0.582)

    def s2_proc(self, e):
        self.afflics.poison(e.name,120,0.582)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
