from core.advbase import *

def module():
    return Renee

class Renee(Adv):
    conf = {}
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `dragon(c3-s-end), x=2
        if self.afflics.frostbite.get()
        `s3
        `s4, cancel or s1.check()
        `s1, cancel
        `s2, cancel
        else
        `s3
        `s4
        `s1, cancel
        `s2, x=1 or s
        end
        `fs, x=5
        """
    conf['coabs'] = ['Blade', 'Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Eugene']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
