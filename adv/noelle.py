
from core.advbase import *

def module():
    return Noelle

class Noelle(Adv):
    conf = {}
    conf['slots.a'] = [
        'A_Dogs_Day',
        'Study_Rabbits',
        'Castle_Cheer_Corps',
        'From_Whence_He_Comes',
        'Bellathorna'
    ]
    conf['slots.d'] = 'Freyja'
    conf['acl'] = """
        `fs, self.fs_prep_c>0 and x=5
        `s1
        `s3
        `s4
        `dodge, fsc
        """
    conf['coabs'] = ['Dagger2','Tobias','Bow']
    conf['share'] = ['Tobias', 'Templar_Hope']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
