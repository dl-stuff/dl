from core.advbase import *
from slot.d import *

def module():
    return Maribelle

class Maribelle(Adv):
    a1 = ('s', 0.4, 'hp100')
    a3 = ('prep','100%')
    conf = {}
    conf['slots.d'] = AC011_Garland()
    conf['acl'] = """
        `dragon(c3 s end), s4.check()
        `s3, not self.s3_buff
        `s4
        `s1
        `s2, cancel
        """
    conf['coabs'] = ['Blade','Akasha','Lin_You']
    conf['share'] = ['Curran']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)