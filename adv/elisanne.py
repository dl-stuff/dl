from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Elisanne

class Elisanne(Adv):
    comment = 'no s2, s!cleo skill after s1'
    a1 = ('bt',0.25)

    conf = {}
    conf['slots.a'] = Beach_Battle()+From_Whence_He_Comes()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `s1
        `s4, s=1
        `s3
        `fs, x=5
    """
    coab = ['Tobias', 'Renee', 'Bow']
    share = ['Summer_Luca', 'Summer_Cleo']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
