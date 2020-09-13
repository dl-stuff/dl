from core.advbase import *
from slot.a import *

def module():
    return Erik

class Erik(Adv):
    conf = {}
    
    conf['slots.a'] = Summer_Paladyns()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end), self.trickery <= 1
        `s3, not buff(s3)
        `s2
        `s1
        `s4, cancel 
        `fs, cancel and charged_in(fs, s2)
    """
    conf['coabs'] = ['Blade','Wand','Delphi']
    conf['share'] = ['Kleimann']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
