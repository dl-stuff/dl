from core.advbase import *

def module():
    return Musashi

class Musashi(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'The_Fires_of_Hate']
    conf['acl'] = """
        `dragon(c3-s-end), s4.check()
        `s3, not buff(s3)
        `s2, s4.check()
        `s4
        `s1, buff(s3)
        """
    conf['coabs'] = ['Eleonora','Dragonyule_Xainfried','Lin_You']
    conf['afflict_res.poison'] = 0
    conf['share'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)