from core.advbase import *

def module():
    return Julietta


class Julietta(Adv):
    conf = {}
    conf['slots.a'] = ['Valiant_Crown','Primal_Crisis']
    conf['slots.d'] = 'Gala_Thor'
    conf['acl'] = """
        `dragon, self.energy()<4
        `s3, not buff(s3)
        `s2
        `s1
        `s4, s1.charged<s1.sp/2
        `fs, x=4 and c_fs(enhanced)>0
        """
    conf['coabs'] = ['Blade','Lucretia','Peony']
    conf['share'] = ['Summer_Cleo']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
