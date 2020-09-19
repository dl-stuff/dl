from core.advbase import *

def module():
    return Orsem

class Orsem(Adv):
    comment = 'no s2'
    
    conf = {}
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `dragon(c3-s-end), self.afflics.frostbite.get() or (not self.afflics.frostbite.get() and fsc)
        `s3
        `s4
        `s1
        `fs, x=5
    """
    conf['coabs'] = ['Blade', 'Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
