from core.advbase import *
from slot.a import *

def module():
    return Althemia

class Althemia(Adv):
    a1 = ('s',0.3,'hp100')
    
    conf = {}
    conf['slot.a'] = Fatalis()
    conf['acl'] = """
        `s3, not this.s3_buff
        `s1
        `s2, x=5
        """

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
