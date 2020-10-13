from core.advbase import *

def module():
    return The_Prince

class The_Prince(Adv):    
    conf = {}
    conf['slots.a'] = [
    'The_Shining_Overlord',
    'The_Red_Impulse',
    'Me_and_My_Bestie',
    'Entwined_Flames',
    'Dueling_Dancers'
    ]
    conf['slots.d'] = 'Gala_Mars'
    conf['acl'] = """
        `dragon, s=2 or s=4
        `s3, not buff(s3)
        `s1
        `s2, fsc
        `s4, fsc
        `fs, x=2
        """
    conf['coabs'] = ['Verica', 'Blade', 'Yuya']
    conf['share'] = ['Gala_Mym']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)