from core.advbase import *

def module():
    return Templar_Hope

class Templar_Hope(Adv):
    conf = {}
    conf['slots.a'] = [
    'The_Shining_Overlord',
    'Flash_of_Genius',
    'Felyne_Hospitality',
    'Sisters_of_the_Anvil',
    'His_Clever_Brother'
    ]
    conf['slots.poison.a'] = [
    'The_Shining_Overlord',
    'Flash_of_Genius',
    'Brothers_in_Arms',
    'The_Plaguebringer',
    'His_Clever_Brother'
    ]
    conf['slots.d'] = 'Vayu'
    conf['acl'] = """
        `dragon(c3-s-end), cancel
        `s3, not buff(s3)
        `s4
        `s2, cancel
        `s1, fsc
        `fs, x=2
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Akasha']
    conf['share'] = ['Xander']
    

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
