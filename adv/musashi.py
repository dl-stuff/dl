from core.advbase import *

def module():
    return Musashi

class Musashi(Adv):
    conf = {}
    conf['slots.a'] = [
    'Resounding_Rendition',
    'Flash_of_Genius',
    'Levins_Champion',
    'The_Plaguebringer',
    'A_Small_Courage'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), s1.check()
        `s3, not buff(s3)
        `s2, s4.check() or s1
        `s1, buff(s3)
        `s4
        `fs, xf=5
        `dodge, fsc
        """
    conf['coabs'] = ['Eleonora','Dragonyule_Xainfried','Akasha']
    conf['share'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)