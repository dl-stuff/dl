from core.advbase import *
from module.bleed import Bleed

def module():
    return Botan

class Botan(Adv):
    conf = {}
    conf['slots.a'] = [
        'Dragon_and_Tamer',
        'The_Fires_of_Hate',
        'Howling_to_the_Heavens',
        'The_Plaguebringer',
        'Catch_Me_in_the_Sunflowers'
    ]
    conf['acl'] = """
        `dragon(c3-s-end),cancel
        `s3, not buff(s3) and prep
        `s2
        `s4
        `s1, bleed_stack<3
        `fs, x=5
    """
    conf['coabs'] = ['Ieyasu','Wand','Bow']
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Curran']
    
if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
