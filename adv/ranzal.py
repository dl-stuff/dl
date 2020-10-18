from core.advbase import *

def module():
    return Ranzal

class Ranzal(Adv):
    conf = {}
    conf['slots.a'] = [
    'Summer_Paladyns',
    'Flash_of_Genius',
    'Kung_Fu_Masters',
    'The_Plaguebringer',
    'Chariot_Drift'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), s1.check()
        `s3, not buff(s3)
        `s1
        `s4, x>2
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Eleonora']
    conf['share'] = ['Curran']
    

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
