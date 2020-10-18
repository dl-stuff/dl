from core.advbase import *

def module():
    return Xainfried

class Xainfried(Adv):
    conf = {}
    conf['slots.a'] = [
    'The_Bridal_Dragon',
    'Dragon_and_Tamer',
    'An_Ancient_Oath',
    'His_Clever_Brother',
    'Dueling_Dancers'
    ]
    conf['slots.d'] = 'Leviathan'
    conf['acl'] = """
        `dragon(c2-s-c2-c2-c2-c2-c2-c2), s=2 or s=4
        `s3, not buff(s3)
        `s2
        `s4
        `s1, fscf
        `fs, x=5
        """
    conf['coabs'] = ['Summer_Celliera', 'Yurius', 'Tiki']
    conf['share'] = ['Gala_Mym']
    

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
