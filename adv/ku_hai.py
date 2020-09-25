from core.advbase import *

def module():
    return Ku_Hai

class Ku_Hai(Adv):
    comment = 'c2+fs during s2'
    conf = {}
    # c1+fs_alt has higher dps and sp rate than c2+fs_alt with or without stellar show  (x)
    # c2+fs_alt fs can init quicker than c1+fs_alt
    conf['slots.a'] = [
    'The_Shining_Overlord',
    'Flash_of_Genius',
    'Moonlight_Party',
    'The_Plaguebringer',
    'Dueling_Dancers'
    ]
    conf['acl'] = '''
        `dragon(c3-s-end),fsc
        `s3, not buff(s3)
        `s4
        `s1
        `s2, fsc
        `fs, x=2 and c_fs(enhanced)
        `fs, x=3
        '''
    conf['coabs'] = ['Dagger','Dragonyule_Xainfried','Akasha']
    conf['share.base'] = ['Rodrigo']
    conf['share.poison'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)