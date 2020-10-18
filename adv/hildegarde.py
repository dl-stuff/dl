from core.advbase import *

def module():
    return Hildegarde

class Hildegarde(Adv):
    conf = {}
    conf['slots.a'] = [
        'Study_Rabbits',
        'Give_Me_Your_Wounded',
        'Castle_Cheer_Corps',
        'From_Whence_He_Comes',
        'Bellathorna'
    ]
    conf['slots.d'] = 'PopStar_Siren'
    conf['acl'] = """
        `dragon
        `s3
        `s4
        `s2
        `s1, not buff(s1)
        """
    conf['coabs'] = ['Dagger2','Tobias','Blade']
    conf['share'] = ['Summer_Luca', 'Patia']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
