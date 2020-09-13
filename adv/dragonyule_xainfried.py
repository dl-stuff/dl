from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Dragonyule_Xainfried

class Dragonyule_Xainfried(Adv):
    comment = 'no s2'

    conf = {}
    conf['slots.a'] = A_Dogs_Day()+Primal_Crisis()
    conf['slots.d'] = Ariel()
    conf['acl'] = """
        `dragon(s-end)
        `s3, not buff(s3)
        `s1
        `s4
        """
    conf['coabs'] = ['Blade','Bow','Tobias']
    conf['share'] = ['Tobias']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)

