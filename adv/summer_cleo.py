from core.advbase import *
from slot.a import *

def module():
    return Summer_Cleo

class Summer_Cleo(Adv):
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon, s=1
        `s3, not buff(s3)
        `s2, s1.charged<s1.sp/3
        `s1
        `s4, cancel
        `fs,x=5
    """
    conf['coabs'] = ['Lucretia','Sharena','Peony']
    conf['share'] = ['Althemia']
    conf['afflict_res.paralysis'] = 0

    def init(self):
        random.seed()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
