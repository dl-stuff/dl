from core.advbase import *
from slot.a import *

def module():
    return Musashi

class Musashi(Adv):
    a1 = ('lo',0.40)
    a3 = ('od',0.08)
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end), s4.check()
        `s3, not self.s3_buff
        `s2, s4.check()
        `s4
        `s1, self.s3_buff
        """
    conf['coabs'] = ['Eleonora','Dragonyule_Xainfried','Lin_You']
    conf['afflict_res.poison'] = 0
    conf['share'] = ['Curran']

    def s1_proc(self, e):
        self.afflics.poison(e.name,110,0.53)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)