from core.advbase import *
from slot.a.all import *
from slot.d.flame import *

def module():
    return Aurien

class Aurien(Adv):
    comment = 'no s1'
    a1 = ('s',0.4,'hp70')

    conf = {}
    conf['slots.a'] = Resounding_Rendition()+The_Fires_of_Hate()
    conf['slots.burn.a'] = Resounding_Rendition()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon.act('c3 s s end'), s
        `s4
        `s3
        `s2, cancel
        """
    conf['afflict_res.burn'] = 0
    conf['coabs'] = ['Blade', 'Marth', 'Wand']
    conf['share'] = ['Summer_Patia']

    def s2_proc(self, e):
        self.afflics.burn(e.name,100,0.803)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)