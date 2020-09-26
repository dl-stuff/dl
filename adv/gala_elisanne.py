from core.advbase import *

def module():
    return Gala_Elisanne

class Gala_Elisanne(Adv):
    comment = 'no s2, s!cleo ss after s1'

    conf = {}
    conf['slots.a'] = [
        'Kung_Fu_Masters',
        'Summer_Paladyns',
        'The_Red_Impulse',
        'From_Whence_He_Comes',
        'Bellathorna'
    ]
    conf['slots.frostbite.a'] = [
        'Kung_Fu_Masters',
        'Summer_Paladyns',
        'The_Red_Impulse',
        'From_Whence_He_Comes',
        'His_Clever_Brother'
    ]
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `dragon(c3-s-end)
        `s3, not buff(s3)
        `s1
        `s2
        `s4
        `fs, x=5
    """
    conf['coabs'] = ['Hunter_Sarisse','Summer_Estelle', 'Renee']
    conf['share'] = ['Gala_Mym']
    
    def prerun(self):
        self.s2.autocharge_init(960).on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)

