from core.advbase import *

def module():
    return Gala_Elisanne

class Gala_Elisanne(Adv):
    comment = 'no s2, s!cleo ss after s1'

    conf = {}
    conf['slots.a'] = ['Beach_Battle', 'The_Chocolatiers']
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `s1
        `s3
        `s4, s=1
        `fsf, x=4
    """
    conf['coabs'] = ['Bow','Tobias', 'Renee']
    conf['share'] = ['Summer_Luca', 'Summer_Cleo']
    
    def prerun(self):
        self.s2.autocharge_init(960).on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)

