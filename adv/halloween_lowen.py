from core.advbase import *
from slot.a.all import The_Bridal_Dragon, From_Whence_He_Comes
from slot.d import PopStar_Siren

def module():
    return Halloween_Lowen

class Halloween_Lowen(Adv):
    comment = 'hlowen dps <= burn DoT'

    conf = {}
    conf['slots.a'] = From_Whence_He_Comes()+The_Bridal_Dragon()
    conf['slots.burn.a'] = conf['slots.a']
    conf['slots.d'] = PopStar_Siren()
    conf['acl'] = """
        `dragon
        `s2, prep or x=5 and mod(maxhp)<1.30
        `s1, x=5
        `s3, x=5
        `s4, x=5
        `fs, s=3 and self.fs_prep_c > 0
    """
    conf['coabs'] = ['Tobias', 'Euden', 'Yuya']
    conf['share'] = ['Patia', 'Summer_Cleo']

    def prerun(self):
        self.hp = 100

if __name__ == '__main__':
    import sys
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
