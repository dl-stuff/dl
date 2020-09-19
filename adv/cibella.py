from core.advbase import *

def module():
    return Cibella

class Cibella(Adv):
    conf = {}
    conf['slots.frostbite.a'] = ['Resounding_Rendition', 'His_Clever_Brother']
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `dragon(c3-s-end),s
        `s4
        `s3, cancel
        `s2, cancel
        `fs, seq=5
        """
    conf['coabs'] = ['Blade', 'Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
