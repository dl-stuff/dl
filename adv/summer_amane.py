from core.advbase import *

def module():
    return Summer_Amane

class Summer_Amane(Adv):
    comment = 'no s1'
    conf = {}
    conf['slots.a'] = [
        'A_Dogs_Day',
        'Study_Rabbits',
        'Castle_Cheer_Corps',
        'From_Whence_He_Comes',
        'Bellathorna'
    ]
    conf['slots.d'] = 'Freyja'
    conf['acl'] = """
        `s3
        `s2
        `s4, x=4
        `fs, self.fs_prep_c>0 and x=4
        `fs, self.fs_prep_c=0 and x>2 and s3.charged>=s3.sp-self.sp_val('fs')
        ## For healing
        #`s1, x=4
        """
    conf['coabs'] = ['Dagger2', 'Tobias', 'Bow']
    conf['share'] = ['Tobias', 'Templar_Hope']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
