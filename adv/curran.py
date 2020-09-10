from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Curran

class Curran(Adv):
    a1 = ('od',0.15)
    a3 = ('lo',0.6)

    conf = {}
    conf['slots.a'] = Summer_Paladyns()+The_Plaguebringer()
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = '''
        `dragon(c3-s-end), s
        `s3, not self.s3_buff
        `s1
        `s2
        `s4
        '''
    conf['coabs'] = ['Curran','Blade','Wand','Bow']
    conf['share'] = ['Kleimann']

    def d_coabs(self):
        if self.sim_afflict:
            self.conf['share'] = ['Veronica']

    def s1_before(self, e):
        with KillerModifier('s1_killer', 'hit', 0.6, ['poison']):
            self.dmg_make(e.name, 2.45)

    def s1_proc(self, e):
        with KillerModifier('s1_killer', 'hit', 0.6, ['poison']):
            self.dmg_make(e.name, 12.70)

    def s2_proc(self, e):
        with Modifier('s2killer', 'poison_killer', 'hit', 1):
            self.dmg_make(e.name, 12.54)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
