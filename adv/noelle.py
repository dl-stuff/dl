
from core.advbase import *

def module():
    return Noelle

class Noelle(Adv):
    comment = 'scleo ss after s1. use Freyja in 4DPS team'

    conf = {}
    conf['slots.a'] = ['A_Dogs_Day', 'Castle_Cheer_Corps']
    conf['slots.poison.a'] = conf['slots.a']
    conf['slots.d'] = 'Ariel'
    conf['acl'] = """
        `fs, self.fs_prep_c>0 and x=5
        `s1
        `s4, s=1
        `s3
        """
    conf['coabs'] = ['Dagger2','Tobias','Bow']
    conf['share'] = ['Summer_Luca', 'Summer_Cleo']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
