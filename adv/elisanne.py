from core.advbase import *

def module():
    return Elisanne

class Elisanne(Adv):
    comment = 'no s2, s!cleo ss after s1'

    conf = {}
    conf['slots.a'] = ['Beach_Battle', 'From_Whence_He_Comes']
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `s1
        `s4, s=1
        `s3
        `fs, x=5
    """
    conf['coabs'] = ['Tobias', 'Renee', 'Bow']
    conf['share'] = ['Summer_Luca', 'Summer_Cleo']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
