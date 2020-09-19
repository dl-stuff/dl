from core.advbase import *

def module():
    return Summer_Amane

class Summer_Amane(Adv):
    comment = 'no s1'
    conf = {}
    conf['slots.a'] = ['A_Dogs_Day', 'Castle_Cheer_Corps']
    conf['slots.poison.a'] = conf['slots.a'] 
    conf['slots.d'] = 'Freyja'
    conf['acl'] = """
        `s3
        `s2
        `s4, cancel
        `fs, self.fs_prep_c>0 and x=4
        `fs, self.fs_prep_c=0 and x>2 and s3.charged>=s3.sp-self.sp_val('fs')
        ## For healing
        #`s1, x=5
        """
    conf['coabs'] = ['Blade', 'Tobias', 'Bow']
    conf['share'] = ['Patia', 'Summer_Luca']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
