from core.advbase import *

def module():
    return Wedding_Aoi

class Wedding_Aoi(Adv):
    conf = {}
    conf['slots.a'] = [
    'Twinfold_Bonds',
    'Flash_of_Genius',
    'Moonlight_Party',
    'The_Plaguebringer',
    'A_Passion_for_Produce'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), x=5
        `s3, not buff(s3)
        `s2
        `s1
        `s4, fsc
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Akasha']
    conf['share.base'] = ['Rodrigo']
    conf['share.poison'] = ['Curran']
    

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
