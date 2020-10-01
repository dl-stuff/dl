from core.advbase import *

def module():
    return Taro

class Taro(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'Breakfast_at_Valerios']
    conf['acl'] = """
        `dragon(c3-s-end),fsc
        `s3, not buff(s3)
        `s4
        `s1,x=5
        `s2,x=5
        `fs,x=5 and buff(s3)
        """
    conf['coabs.base'] = ['Wand','Dagger','Axe2']
    conf['coabs.poison'] = ['Wand','Dagger','Forte']
    conf['share'] = ['Curran']

    conf['mbleed'] = True


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
