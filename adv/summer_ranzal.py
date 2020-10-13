from core.advbase import *

def module():
    return Summer_Ranzal

class Summer_Ranzal(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'Breakfast_at_Valerios']
    conf['slots.frostbite.a'] = ['Primal_Crisis', 'His_Clever_Brother']
    conf['slots.d'] = 'Leviathan'
    conf['acl'] = """
        `dragon
        `s3
        `s4
        `s2
        """
    conf['coabs'] = ['Xander', 'Dagger', 'Tiki']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
