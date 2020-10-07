from core.advbase import *
from module.x_alt import *

def module():
    return Celliera

class Celliera(Adv):
    conf = {}
    conf['slots.d'] = 'Siren'
    conf['slots.a'] = ['Primal_Crisis', 'His_Clever_Brother']
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['acl'] = """
        `s2, not buff(s2)
        `s3, cancel
        `s4, x=4
        `s1
    """
    conf['coabs'] = ['Renee', 'Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

    def s2_proc(self, e):
        if e.group == 'enhanced':
            self.dragonform.disabled = False
        else:
            self.dragonform.disabled = True

    def fs_enhanced_proc(self, e):
        self.dragonform.disabled = False

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)