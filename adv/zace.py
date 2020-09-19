from core.advbase import *

def module():
    return Zace

class Zace(Adv):
    conf = {}
    conf['slots.a'] = ['Dragon_and_Tamer', 'The_Fires_of_Hate']
    conf['acl'] = """
        `dragon(c3-s-end), fsc
        `s3, not buff(s3)
        `s4
        `s1, cancel
        `s2, x>=3
        `fs, x=5
    """
    conf['coabs'] = ['Ieyasu','Wand','Bow']
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
