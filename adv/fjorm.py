from core.advbase import *
from slot.a import *

def module():
    return Fjorm

class Fjorm(Adv):
    comment = 'last bravery once at start'

    a3 = [('prep',1.00), ('scharge_all', 0.05)]

    conf = {}
    conf['slots.a'] = Dragon_and_Tamer()+His_Clever_Brother()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        queue prep
        `s3;s1;s4;s2
        end
        `dragon.act('c3 s c1 end'),cancel
        `s3
        `s4
        `s1, cancel
        `s2, s=1
        `fs, x=5
    """
    coab = ['Blade', 'Summer_Estelle', 'Renee']
    share = ['Gala_Elisanne', 'Eugene']

    def prerun(self):
        Teambuff('last_bravery',0.3,15).on()

    def s1_proc(self, e):
        self.afflics.frostbite(e.name,120,0.41)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
