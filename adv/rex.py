from core.advbase import *

def module():
    return Rex

class Rex(Adv):
    conf = {}
    conf['slots.a'] = ['Summer_Paladyns', 'Primal_Crisis']
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `dragon(c3-s-end), cancel
        `s3
        `s4
        `s1
        `s2, cancel
        `fs, cancel and charged_in(fs, s1)
    """
    conf['coabs'] = ['Blade', 'Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)