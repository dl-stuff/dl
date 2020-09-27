from core.advbase import *

import random
random.seed()

def module():
    return Gala_Cleo


class Gala_Cleo(Adv):
    comment = '(the true cleo is here)'
    conf = {}
    conf['slots.a'] = [
        'Candy_Couriers',
        'Flash_of_Genius',
        'Moonlight_Party',
        'The_Plaguebringer',
        'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), x=5 and self.trickery <= 1
        `s3, not buff(s3)
        `fs, s1.charged>=s1.sp and c_fs(gleozone) > 0
        if x=5 or x=4 or fsc or s
        `s4
        `s2
        end
        `s1, s or fsc
    """
    conf['coabs'] = ['Blade','Bow','Dagger']
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
