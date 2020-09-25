from core.advbase import *

def module():
    return Nicolas

class Nicolas(Adv):
    conf = {}
    conf['slots.a'] = [
    'Candy_Couriers',
    'Flash_of_Genius',
    'Brothers_in_Arms',
    'The_Plaguebringer',
    'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon(c3-s-end),s1.check()
        `s3, not buff(s3)
        `s1
        `s4
        `s2, cancel
        """
    conf['coabs'] = ['Blade','Akasha','Bow']
    conf['share.base'] = ['Rodrigo']
    conf['share.poison'] = ['Curran']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)

