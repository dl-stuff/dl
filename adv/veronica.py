from core.advbase import *

def module():
    return Veronica

class Veronica(Adv):
    comment = 'last destruction team DPS not considered'
    conf = {}
    conf['slots.a'] = ['Candy_Couriers', 'Primal_Crisis']
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = """
        `dragon(c3-s-end), ((self.hp>0 and s) or (self.hp=0 and x=5))
        queue prep and not buff(s3)
        `s3;s4;s2;s1
        end
        `s1
        `s4
        """
    conf['coabs'] = ['Berserker','Curran','Summer_Patia']
    conf['share.base'] = ['Kleimann']
    conf['share.poison'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
