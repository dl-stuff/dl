from core.advbase import *

def module():
    return Lea

class Lea(Adv):        
    conf = {}
    conf['slots.a'] = ['The_Shining_Overlord', 'Me_and_My_Bestie']
    conf['acl'] = """
        `dragon
        `s3, not buff(s3) and fsc
        `s4, cancel
        `s1, fsc
        `fs, x=2
        """
    conf['coabs'] = ['Blade', 'Wand', 'Marth']
    conf['share'] = ['Kleimann']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)