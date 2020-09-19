from core.advbase import *

def module():
    return Curran

class Curran(Adv):
    conf = {}
    conf['slots.a'] = ['Summer_Paladyns', 'The_Plaguebringer']
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = '''
        `dragon(c3-s-end), s
        `s3, not buff(s3)
        `s1
        `s2
        `s4
        '''
    conf['coabs'] = ['Curran','Blade','Wand','Bow']
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Veronica']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
