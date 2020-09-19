from core.advbase import *

def module():
    return Rodrigo

class Rodrigo(Adv):
    conf = {}
    conf['slots.a'] = ['The_Shining_Overlord', 'The_Fires_of_Hate']
    conf['acl'] = """
        `dragon(c3-s-end),fsc
        `s3, fsc and not buff(s3)
        `s4
        `s1, cancel and buff(s3)
        `s2, fsc
        `fs, x=2 and s1.charged > 841
        `fs, x=3
        """
    conf['coabs'] = ['Ieyasu','Wand','Forte']
    conf['share'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
