from core.advbase import *

def module():
    return Pia

class Pia(Adv):
    conf = {}
    conf['slots.a'] = [
    'Dragon_and_Tamer',
    'Flash_of_Genius',
    'Astounding_Trick',
    'The_Plaguebringer',
    'Dueling_Dancers'
    ]
    conf['slots.d'] = 'Vayu'
    conf['acl'] = """
        `dragon(c3-s-end), not energy()=5 and s1.check()
        `s3, not buff(s3)
        `s2
        `s4
        `s1, buff(s3)
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Bow']
    conf['share'] = ['Tobias']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)