from core.advbase import *

def module():
    return Catherine

class Catherine(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'Memory_of_a_Friend']
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `dragon(c3-s-end), s
        `s3
        `s4
        `s2, s2.phase='escort3' and energy()>=5
        `s1, xf
    """
    conf['coabs'] = ['Dragonyule_Cleo', 'Hunter_Sarisse', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

    # def __init__(self, conf=None, cond=None):
    #     super().__init__(conf=conf, cond=cond)
    #     del self.conf['x4']
    #     del self.conf['x5']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
