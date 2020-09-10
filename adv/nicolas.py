from core.advbase import *

def module():
    return Nicolas

class Nicolas(Adv):
    conf = {}
    conf['acl'] = """
        `dragon(c3-s-end),s4.check()
        `s3, not buff(s3)
        `s4
        `s2
        `s1, x>2
        """
    conf['coabs'] = ['Blade','Akasha','Lin_You']
    conf['share'] = ['Curran']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)

