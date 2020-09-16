from core.advbase import *
from slot.a import *

def module():
    return Sinoa

class Sinoa(Adv):
    conf = {}
    conf['acl'] = '''
        `dragon, s=1
        `s3, not buff(s3)
        `s1
        `s2
        `s4
    '''
    conf['coabs'] = ['Yuya', 'Gala_Sarisse', 'Marth']
    conf['share'] = ['Kleimann']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
