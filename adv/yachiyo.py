from core.advbase import *
from slot.a import *
from slot.w import *

def module():
    return Yachiyo

class Yachiyo(Adv):
    conf = {}
    conf['slots.a'] = RR()+SotS()
    conf['acl'] = """
        `dragon, s
        `s3, not buff(s3)
        `fs, c_fs(enhanced) and x=5
        `s1
        `s4, cancel
        `s2, x=5
        """
    conf['coabs.base'] = ['Lucretia','Malora','Peony']
    conf['coabs.paralysis'] = ['Lucretia','Malora','Peony']
    conf['share'] = ['Ranzal']
    conf['afflict_res.paralysis'] = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
