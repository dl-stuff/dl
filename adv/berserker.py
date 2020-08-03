from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Berserker

class Berserker(Adv):
    a3 = ('lo',0.3)
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+Primal_Crisis()
    conf['slots.poison.a'] = The_Shining_Overlord()+Primal_Crisis()
    conf['acl'] = """
        `dragon.act('c3 s end'),fsc
        `s3, not self.s3_buff and fsc
        `s4
        `s1,fsc
        `fs, x=3
        """
    coab = ['Berserker','Ieyasu','Wand','Curran']
    share = ['Curran']

    def s1_proc(self, e):
        Debuff(e.name, 0.05, 10, 0.4, 'attack')

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
