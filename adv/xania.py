from core.advbase import *

def module():
    return Xania

class Xania(Adv):
    conf = {}
    conf['slots.a'] = [
        'Me_and_My_Bestie',
        'Candy_Couriers',
        'The_Red_Impulse',
        'Dueling_Dancers',
        'Entwined_Flames'
    ]
    conf['acl'] = """
        `dragon(c3-s-s-end),s
        `s3, not buff(s3) and x=5
        `s1
        `s4,cancel
        `s2,x=5
        """
    conf['coabs'] = ['Blade', 'Marth', 'Joe']
    conf['share'] = ['Kleimann']
    conf['afflict_res.burn'] = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
