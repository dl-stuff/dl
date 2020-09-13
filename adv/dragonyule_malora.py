from core.advbase import *
from slot.a import *

def module():
    return Dragonyule_Malora

class Dragonyule_Malora(Adv):
    conf = {}
    conf['slots.a'] = Summer_Paladyns() + Primal_Crisis()
    conf['acl'] = """
        `dragon, s
        `s3, not buff(s3)
        `s2, self.def_mod()!=1 and energy()>=5
        `s4, cancel
        `s1, x=4
        """
    conf['coabs'] = ['Lucretia','Blade','Peony']
    conf['share'] = ['Sha_Wujing']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)