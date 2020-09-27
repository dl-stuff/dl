from core.advbase import *

def module():
    return Maribelle

class Maribelle(Adv):
    conf = {}
    conf['slots.a'] = [
    'Candy_Couriers',
    'Flash_of_Genius',
    'Moonlight_Party',
    'The_Plaguebringer',
    'Dueling_Dancers'
    ]
    conf['slots.d'] = 'Vayu'
    conf['acl'] = """
        `dragon(c3-s-end), s4.check()
        `s3, not buff(s3)
        `s1
        `s2, cancel
        `s4
        """
    conf['coabs'] = ['Blade','Akasha','Lin_You']
    conf['share.base'] = ['Rodrigo']
    conf['share.poison'] = ['Curran']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)