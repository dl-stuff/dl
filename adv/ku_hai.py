from core.advbase import *

def module():
    return Ku_Hai

class Ku_Hai(Adv):
    comment = 'c2+fs during s2'
    conf = {}
    # c1+fs_alt has higher dps and sp rate than c2+fs_alt with or without stellar show  (x)
    # c2+fs_alt fs can init quicker than c1+fs_alt
    conf['slots.a'] = ['Mega_Friends', 'Primal_Crisis']
    conf['slots.poison.a'] = ['Mega_Friends', 'The_Fires_of_Hate']
    conf['slots.d'] = 'AC011_Garland'
    conf['slots.poison.d'] = 'Pazuzu'
    conf['acl'] = '''
        `dragon(c3-s-end),fsc
        `s3, not buff(s3)
        `s4
        `s2
        `s1, fsc
        `fs, x=2 and c_fs(enhanced)
        `fs, x=3
        '''
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Akasha']
    conf['share'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)