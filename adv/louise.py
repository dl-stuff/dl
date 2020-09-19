from core.advbase import *

def module():
    return Louise

class Louise(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'The_Fires_of_Hate']
    conf['acl'] = """
        `dragon(c3-s-end), s2.check()
        `s3, not buff(s3)
        `s4, fsc
        `s1
        `s2
        `fs, x=4
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']
    conf['afflict_res.poison'] = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)