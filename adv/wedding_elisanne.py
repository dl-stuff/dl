from core.advbase import *
from slot.a import *

def module():
    return Wedding_Elisanne


class Wedding_Elisanne(Adv):
    a1 = ('sp',0.08)
    a3 = ('bc',0.13)

    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+Primal_Crisis()
    conf['acl'] = """
        `dragon.act("c3 s end"), s4.check()
        `s3, not self.s3_buff
        `s2
        `s4
        `s1, fsc
        `fs, x=2
    """
    coab = ['Blade','Dragonyule_Xainfried','Lin_You']
    share = ['Curran']

    def s2_proc(self, e):
        if self.condition(f'{e.name} defdown for 10s'):
            self.s2_debuff = Debuff(e.name,0.15,10,1).no_bufftime().on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
