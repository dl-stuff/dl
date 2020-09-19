from core.advbase import *

def module():
    return Wedding_Elisanne


class Wedding_Elisanne(Adv):
    conf = {}
    conf['slots.a'] = ['The_Shining_Overlord', 'Primal_Crisis']
    conf['acl'] = """
        `dragon(c3-s-end), s4.check()
        `s3, not buff(s3)
        `s2
        `s4
        `s1, fsc
        `fs, x=2
    """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
