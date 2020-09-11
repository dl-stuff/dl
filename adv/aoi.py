from core.advbase import *
from slot.a import *

def module():
    return Aoi

class Aoi(Adv):
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon, s=2
        `s3, not buff(s3)
        `s4
        `s1
        `s2
    """
    conf['coabs'] = ['Wand', 'Marth', 'Yuya']
    conf['share'] = ['Kleimann']
    conf['afflict_res.burn'] = 0

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)