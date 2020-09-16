from core.advbase import *
from slot.a import *

def module():
    return Xuan_Zang

class Xuan_Zang(Adv):    
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+The_Fires_of_Hate()
    conf['slots.burn.a'] = Resounding_Rendition()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon, s=2
        `s3, not buff(s3) and fsc
        `s4
        `s2
        `s1,fsc
        `fs, x=5
        """
    conf['coabs'] = ['Blade', 'Marth', 'Gala_Sarisse']
    conf['share'] = ['Kleimann']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
