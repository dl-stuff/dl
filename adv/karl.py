from core.advbase import *

def module():
    return Karl

class Karl(Adv):
    conf = {}
    conf['slots.a'] = ['Primal_Crisis', 'The_Lurker_in_the_Woods']
    conf['slots.d'] = 'Gala_Mars'
    conf['acl'] = """
        `dragon, s=2
        `s3, not buff(s3)
        `s2, cancel
        `s4, cancel
        `fs, x=2
    """
    conf['coabs'] = ['Blade', 'Dagger2', 'Bow']
    conf['share'] = ['Summer_Patia']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)