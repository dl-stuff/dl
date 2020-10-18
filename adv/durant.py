from core.advbase import *

def module():
    return Durant

class Durant(Adv):
    conf = {}
    conf['slots.a'] = [
        'Flash_of_Genius',
        'Moonlight_Party',
        'Proper_Maintenance',
        'The_Plaguebringer',
        'From_Whence_He_Comes'
    ]
    conf['slots.d'] = 'Epimetheus'
    conf['acl'] = """
        `dragon, s=1
        `s3, not buff(s3)
        `s1
        `s2, x=5
        `s4
    """
    conf['coabs'] = ['Dagger2', 'Tobias', 'Axe2']
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Curran']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
