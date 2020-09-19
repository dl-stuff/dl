from core.advbase import *

def module():
    return Templar_Hope

class Templar_Hope(Adv):
    conf = {}
    conf['slots.a'] = ['The_Shining_Overlord', 'Primal_Crisis']
    conf['slots.d'] = 'AC011_Garland'
    conf['acl'] = """
        `dragon(c3-s-c3-c3-end), cancel
        `s3, not buff(s3)
        `s4
        `s2, cancel
        `fs, x=2
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']
    

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
