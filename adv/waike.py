from core.advbase import *

def module():
    return Waike

class Waike(Adv):
    conf = {}
    conf['slots.a'] = ['Forest_Bonds', 'Primal_Crisis']
    conf['slots.frostbite.a'] = ['Forest_Bonds', 'His_Clever_Brother']
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `dragon(c3-s-end)
        `s3
        `s4
        `s1, cancel
        `s2, cancel
        `fs, seq=4
        """
    conf['coabs'] = ['Blade', 'Xander', 'Summer_Estelle']
    conf['afflict_res.bog'] = 100
    conf['share'] = ['Gala_Elisanne', 'Ranzal']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
