from core.advbase import *

def module():
    return Vida

class Vida(Adv):
    comment = 'no s2'
    conf = {}
    conf['acl'] = """
        `dragon(c3-s-end), s or fsc
        `s3, not buff(s3) and x=5
        `s4
        `s1, cancel
        `fs, x=5
        """
    conf['coabs'] = ['Ieyasu','Wand','Forte']
    conf['share'] = ['Kleimann']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
