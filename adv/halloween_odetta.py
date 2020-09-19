from core.advbase import *

def module():
    return Halloween_Odetta

class Halloween_Odetta(Adv):
    conf = {}
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `dragon(c3-s-end), s=2
        `s3, cancel
        `s2, cancel
        `s4, fsc
        `s1, fsc
        `fs, x=3 and not self.afflics.frostbite.get()
        `fs, x=2 and self.afflics.frostbite.get()
    """
    conf['coabs'] = ['Summer_Estelle','Blade','Renee']
    conf['share'] = ['Gala_Elisanne', 'Eugene']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)