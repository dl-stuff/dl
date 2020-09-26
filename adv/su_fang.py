from core.advbase import *

def module():
    return Su_Fang

class Su_Fang(Adv):
    conf = {}
    conf['slots.a'] = [
    'Twinfold_Bonds',
    'Flash_of_Genius',
    'Moonlight_Party',
    'The_Plaguebringer',
    'A_Passion_for_Produce'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), s4.check()
        `s3, not buff(s3) and fscf
        `s4
        `s1, cancel and buff(s3) 
        `s2, fscf
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Akasha']
    conf['share'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
