from core.advbase import *

def module():
    return Templar_Hope

class Templar_Hope(Adv):
    conf = {}
    conf['slots.a'] = [
    'The_Shining_Overlord',
    'Flash_of_Genius',
    'Brothers_in_Arms',
    'The_Plaguebringer',
    'Dueling_Dancers'
    ]
    conf['slots.d'] = 'Vayu'
    conf['acl'] = """
        `dragon(c3-s-end), cancel
        `s3, not buff(s3)
        `s4
        `s2, fsc
        `s1, fsc
        `fs, x=2
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Bow']
    conf['share.base'] = ['Rodrigo']
    conf['share.poison'] = ['Curran']
    

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
