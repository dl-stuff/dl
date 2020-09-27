from core.advbase import *

def module():
    return Delphi

class Delphi(Adv):
    conf = {}
    conf['slots.a'] = [
        'Twinfold_Bonds',
        'Flash_of_Genius',
        'The_Lurker_in_the_Woods',
        'The_Plaguebringer',
        'Dueling_Dancers'
    ]
    conf['slots.d'] = 'Ramiel'
    conf['acl'] = """
        `dragon(c3-s-end), s=1
        `s3, not buff(s3)
        `s1
        `s4
        `s2, not c_fs(enhanced) and (s1.charged <= ((s1.sp/13)*9))
        `fs, x=2
    """
    conf['coabs'] = ['Ieyasu','Gala_Alex','Forte']
    conf['share'] = ['Karl']
    conf['afflict_res.poison'] = 0

    def prerun(self):        
        self.s1.autocharge_init(80000).on()
        self.s2.autocharge_init(50000).on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
