from core.advbase import *

def module():
    return Berserker

class Berserker(Adv):
    conf = {}
    conf['slots.a'] = [
        'The_Shining_Overlord',
        'Flash_of_Genius',
        'Moonlight_Party',
        'The_Plaguebringer',
        'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon(c3-s-end),fsc
        `s3, not buff(s3) and fsc
        `s2, cancel
        `s4
        `s1, cancel
        `fs, x=2
        """
    conf['coabs'] = ['Berserker','Ieyasu','Wand','Curran']
    conf['share.base'] = ['Rodrigo']
    conf['share.poison'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
