from core.advbase import *

def module():
    return Joachim

class Joachim(Adv):    
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'The_Fires_of_Hate']
    conf['acl'] = '''
        `dragon(c3-s-end)
        `s3, not buff(s3)
        `s2, s=1
        `s1
        `s4
    '''
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['afflict_res.poison'] = 0
    conf['share'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)