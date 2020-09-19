from core.advbase import *

def module():
    return Dragonyule_Nefaria

class Dragonyule_Nefaria(Adv):
    conf = {}
    conf['slots.a'] = ['Forest_Bonds', 'Primal_Crisis']
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `dragon(c3-s-end),s 
        `s3
        `s4
        `s1
        `fs, seq=4
    """
    conf['coabs'] = ['Blade', 'Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)