from core.advbase import *


def module():
    return Emma

class Emma(Adv):
    conf = {}
    conf['slots.d'] = 'Horus'
    conf['slots.a'] = ['Castle_Cheer_Corps', 'From_Whence_He_Comes']
    conf['slots.burn.a'] = conf['slots.a']
    conf['acl'] = """
        `s4, s=1
        `s1
        `s3, fscf
        `fs, x=5
        """
    conf['coabs'] = ['Tobias', 'Dagger2', 'Bow']
    conf['share'] = ['Summer_Luca','Summer_Cleo']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
