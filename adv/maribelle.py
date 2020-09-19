from core.advbase import *

def module():
    return Maribelle

class Maribelle(Adv):
    conf = {}
    conf['slots.d'] = 'AC011_Garland'
    conf['acl'] = """
        `dragon(c3-s-end), s4.check()
        `s3, not buff(s3)
        `s4
        `s1
        `s2, cancel
        """
    conf['coabs'] = ['Blade','Akasha','Lin_You']
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Curran']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)