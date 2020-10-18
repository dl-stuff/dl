from core.advbase import *

def module():
    return Fleur

class Fleur(Adv):
    conf = {}
    conf['slots.a'] = ['Twinfold_Bonds', 'Spirit_of_the_Season']
    conf['acl'] = '''
        `dragon, cancel
        `s3, not buff(s3)
        `s2, s=1
        `s1
        `s4, xf or fscf
        `fs, x=5
    '''
    conf['coabs'] = ['Lucretia','Sharena','Peony']
    conf['share'] = ['Kleimann']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)