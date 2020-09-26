from core.advbase import *
from module.bleed import Bleed, mBleed

def module():
    return Victor

class Victor(Adv):
    conf = {}
    conf['slots.a'] = [
    'Resounding_Rendition',
    'Flash_of_Genius',
    'Levins_Champion',
    'The_Plaguebringer',
    'A_Small_Courage'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), s1.check() and bleed_stack<3
        `s3, not buff(s3)
        `s1, bleed_stack < 3
        `s4, x=5
        `s2, x=5
        """
    conf['coabs'] = ['Akasha','Dragonyule_Xainfried','Lin_You']
    conf['share.base'] = ['Rodrigo']
    conf['share.poison'] = ['Curran']

    conf['mbleed'] = True


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
