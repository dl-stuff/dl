from core.advbase import *

def module():
    return Dragonyule_Xainfried

class Dragonyule_Xainfried(Adv):
    comment = 'no s2'
    conf = {}
    conf['slots.a'] = [
        'Study_Rabbits',
        'Jewels_of_the_Sun',
        'Castle_Cheer_Corps',
        'From_Whence_He_Comes',
        'Bellathorna'
    ]
    conf['slots.d'] = 'Freyja'
    conf['acl'] = """
        `s4
        `s1
        `s3, xf>2 or fsc
        `fs, x=5
        `dodge,fsc
        """
    conf['coabs'] = ['Dagger2','Bow','Tobias']
    conf['share'] = ['Marty','Tobias']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)

