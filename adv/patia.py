from core.advbase import *
from module.bleed import Bleed

def module():
    return Patia

class Patia(Adv):
    conf = {}
    conf['slots.a'] = ['Proper_Maintenance', 'From_Whence_He_Comes']
    conf['slots.poison.a'] = conf['slots.a']
    conf['slots.d'] = 'Azazel'
    conf['acl'] = """
        `dragon(c3-s-end), fscf
        `s3, not buff(s3)
        `s1
        `s4, x=4
        `fs, x=5
    """
    conf['coabs'] = ['Audric','Bow','Tobias']
    conf['share'] = ['Karl']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
