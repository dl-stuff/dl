from core.advbase import *

def module():
    return Renelle

class Renelle(Adv):    
    conf = {}
    conf['slots.a'] = ['Twinfold_Bonds', 'Me_and_My_Bestie']
    conf['acl'] = """
        `dragon
        `s3, not buff(s3)
        `s2
        `s4,cancel
        `s1,cancel
        `fs, x=5
        """
    conf['afflict_res.burn'] = 0
    conf['coabs'] = ['Blade', 'Marth', 'Wand']
    conf['share'] = ['Kleimann']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
