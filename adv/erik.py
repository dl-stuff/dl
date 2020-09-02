from core.advbase import *
from slot.a import *

def module():
    return Erik

class Erik(Adv):
    a1 = ('fs',0.30)
    conf = {}
    
    conf['slots.a'] = Summer_Paladyns()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon.act("c3 s end"), self.trickery <= 1
        `s3, not self.s3_buff
        `s2
        `s1
        `s4, cancel 
        `fs, cancel and s2.charged>=s2.sp-self.sp_val('fs')
    """
    conf['coabs'] = ['Blade','Wand','Delphi']
    conf['share'] = ['Kleimann']

    def s1_proc(self, e):
        with KillerModifier('s1_killer', 'hit', 0.5, ['poison']):
            self.dmg_make(e.name, 15.84)

    def s2_proc(self, e):
        with KillerModifier('s2_killer', 'hit', 0.5, ['poison']):
            self.dmg_make(e.name, 17.16)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
