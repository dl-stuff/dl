from core.advbase import *

def module():
    return Hawk

class Hawk(Adv):    
    conf = {}
    conf['slots.a'] = [
    'Forest_Bonds',
    'Flash_of_Genius',
    'Dear_Diary',
    'The_Plaguebringer',
    'Chariot_Drift'
    ]
    conf['slots.d'] = 'Vayu'
    conf['acl'] = """
        # queue self.duration<=60 and prep and self.afflics.stun.resist
        # s2; s3; fs; s1, fsc; fs; s1, fsc; s1, cancel; s2, cancel
        # end
        `s3, not buff(s3)
        `dragon(c3-s-end), s and self.duration >= 120
        `s2, c_fs(enhanced)=0 or self.s2.phase=1
        `fs, (s1.check() and c_fs(enhanced)>1) or (x=4 and self.s2.phase=0 and c_fs(enhanced)>0)
        `s4, s or x=5
        `s1, fsc or s=1 or s=4
    """

    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Sylas']
    conf['share'] = ['Curran']
        

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
