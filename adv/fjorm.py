from core.advbase import *
from slot.d import *
from slot.a import *

def module():
    return Fjorm

class Fjorm(Adv):
    comment = 'last bravery once at start'
    conf = {}
    conf['slots.a'] = Dragon_and_Tamer()+His_Clever_Brother()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        queue prep
        `s3;s1;s4;s2
        end
        `dragon(c3-s-c1-end),cancel
        `s3
        `s4
        `s1, cancel
        `s2, s=1
        `fs, x=5
    """
    conf['coabs'] = ['Blade', 'Summer_Estelle', 'Renee']
    conf['share'] = ['Gala_Elisanne', 'Eugene']

    def prerun(self):
        Teambuff('last_bravery',0.3,15).on()
        Teambuff('last_bravery_defense', 0.40, 15, 'defense').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
