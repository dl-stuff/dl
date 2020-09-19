from core.advbase import *

def module():
    return Pia

class Pia(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'Breakfast_at_Valerios']
    conf['slots.d'] = 'Vayu'
    conf['acl'] = """
        `dragon(c3-s-end), s4.check()
        `s3, not buff(s3)
        `s2, self.energy() = 4 and s4.check()
        `s4
        `s2,fsc and self.energy()<4
        `s1, buff(s3)
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)