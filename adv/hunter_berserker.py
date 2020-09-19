from core.advbase import *

def module():
    return Hunter_Berserker


class Hunter_Berserker(Adv):
    comment = 'needs combo time from chain coability to keep combo & do c1 after s2'
    conf = {}
    conf['slots.a'] = ['The_Lurker_in_the_Woods', 'Primal_Crisis']
    conf['slots.d'] = 'Dreadking_Rathalos'
    conf['acl'] = """
        `s3, not buff(s3)
        `s1, fsc
        `s4, fsc
        queue self.s2.check()
        `s2
        `fs3, x=1
        end
        `dodge, fsc
        `fs3
    """
    conf['coabs'] = ['Nobunaga','Grace','Marth']
    conf['share'] = ['Hunter_Sarisse']

    # def prerun(self):
    #     self.a3_crit = Modifier('a3', 'crit', 'chance', 0)
    #     self.a3_crit.get = self.a3_crit_get
    #     self.a3_crit.on()

    # def a3_crit_get(self):
    #     return (self.mod('def') != 1) * 0.20


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)