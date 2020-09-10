from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Valentines_Melody

class Valentines_Melody(Adv):
    comment = 'c4fsf c5 c4 s1'
    a1 = ('affteam_poison', 0.10, 10, 5)
    a3 = ('k_poison',0.3)

    conf = {}
    conf['slots.a'] = Resounding_Rendition()+The_Fires_of_Hate()
    conf['slots.d'] = Ariel()
    conf['acl'] = """
        `dragon(c3-s-end),s=1
        `s3, not self.s3_buff
        `s1
        `s4
        `s2, cancel
        """
    conf['coabs'] = ['Blade','Eleonora','Dragonyule_Xainfried']
    conf['share'] = ['Curran']
    conf['afflict_res.poison'] = 0

    def init(self):
        self.slots.c.coabs['Axe2'] = [None, 'axe2']

    def s1_proc(self, e):
        if self.condition(f'{e.name} defdown for 10s'):
            Debuff(e.name,0.15,10,1).no_bufftime().on()

    def s2_proc(self, e):
        self.afflics.poison(e.name, 120, 0.582)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
    