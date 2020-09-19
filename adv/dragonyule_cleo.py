from core.advbase import *

def module():
    return Dragonyule_Cleo

class Dragonyule_Cleo(Adv):
    conf = {}
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `dragon(c3-s-end)
        `s1
        `s4
        `s3, cancel
        `s2, cancel
        `fs, xf=4
    """
    conf['coabs'] = ['Blade', 'Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Eugene']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
