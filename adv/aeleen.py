from core.advbase import *

def module():
    return Aeleen

class Aeleen(Adv):
    conf = {}
    conf['slots.a'] = [
    'Dragon_and_Tamer',
    'Flash_of_Genius',
    'Moonlight_Party',
    'The_Plaguebringer',
    'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), s4.check()
        `s3, not buff(s3)
        `s1, buff(s3)
        `s4, x=5 andself.sim_afflict
        `s4, not self.sim_afflict
        `s2, xf or fscf
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['share.base'] = ['Rodrigo']
    conf['share.poison'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
