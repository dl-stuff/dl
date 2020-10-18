from core.advbase import *

def module():
    return Eleonora

class Eleonora(Adv):
    conf = {}
    conf['slots.a'] = [
    'Forest_Bonds',
    'Flash_of_Genius',
    'Dear_Diary',
    'The_Plaguebringer',
    'Chariot_Drift'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), s4.check()
        `s3, not buff(s3)
        `s2
        `s4, xf or fscf or s
        `s1, xf or fscf
        `fs, x=5
        `dodge, fscf
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Akasha']
    conf['share'] = ['Curran']
    

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)