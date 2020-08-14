from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Templar_Hope

class Templar_Hope(Adv):
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+Primal_Crisis()
    conf['slots.d'] = AC011_Garland()
    conf['acl'] = """
        `dragon.act('c3 s c3 c3 end')
        `s3, not self.s3_buff
        `s4
        `s2, cancel
        `fs, x=2
        """
    coab = ['Blade','Dragonyule_Xainfried','Lin_You']
    share = ['Curran']
    
    def s1_proc(self, e):
        Teambuff(e.name, 0.25, 15, 'defense').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
