from core.advbase import *

def module():
    return Ramona

class Ramona(Adv):
    conf = {}
    conf['slots.a'] = ['Summer_Paladyns', 'Primal_Crisis']
    conf['acl'] = """
        `dragon(c3-s-s-end),s=1 and not s4.check()
        `s3, not buff(s3)
        `s2, s1.check()
        `s4, s=1
        `s1(all)
        """
    conf['coabs'] = ['Gala_Sarisse', 'Wand', 'Marth']
    conf['share'] = ['Summer_Patia']


    def s(self, n, s1_kind=None):
        if n == 1 and s1_kind == 'all':
            self.current_s['s1'] = s1_kind
        else:
            self.current_s['s1'] = 'default'
        return super().s(n)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
