from core.advbase import *

def module():
    return Wu_Kong

class Wu_Kong(Adv):
    conf = {}
    conf['slots.a'] = ['Twinfold_Bonds', 'The_Fires_of_Hate']
    conf['slots.paralysis.a'] = ['Twinfold_Bonds', 'Spirit_of_the_Season']
    conf['acl'] = """
        `dragon, s
        `s3, not buff(s3)
        `s4
        `s2
        `s1
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Lucretia','Peony']
    conf['share'] = ['Kleimann']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)