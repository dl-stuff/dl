from core.advbase import *

def module():
    return Sophie

class Sophie(Adv):
    comment = 'no s1'

    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'The_Fires_of_Hate']
    conf['acl'] = """
        `dragon(c3-s-c2-end), s4.check()
        `s4
        `s3
        `s2, x>1
        """
    conf['coabs'] = ['Blade', 'Dragonyule_Xainfried', 'Lin_You']
    conf['afflict_res.poison'] = 0
    conf['share'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
