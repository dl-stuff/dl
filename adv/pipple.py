from core.advbase import *

def module():
    return Pipple

class Pipple(Adv):
    conf = {}
    conf['slots.a'] = ['Proper_Maintenance', 'Brothers_in_Arms']
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `dragon(c3-s-end),x=5
        `s2, (x=5 or s) and self.energy()<5
        `s4
        `s3, cancel
        `s1, x>2
        """
    conf['coabs'] = ['Tiki', 'Renee', 'Tobias']
    conf['share'] = ['Summer_Luca','Patia']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)