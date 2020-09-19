from core.advbase import *

def module():
    return Orion

class Orion(Adv):
    conf = {}
    conf['acl'] = """
        `dragon(c3-s-end), self.sim_afflict or self.trickery <= 1
        `s3, not buff(s3)
        `s4
        `s2, x=4 or x=5
        `s1, buff(s3) and cancel
        `fs, x=5
    """
    conf['coabs.base'] = ['Ieyasu','Wand','Axe2']
    conf['coabs.poison'] = ['Ieyasu','Wand','Forte']
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
