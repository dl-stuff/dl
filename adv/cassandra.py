from core.advbase import *

def module():
    return Cassandra

class Cassandra(Adv):
    conf = {}
    conf['slots.a'] = ['Candy_Couriers', 'Primal_Crisis']
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = """
        `dragon(c3-s-end), x=5
        `s3, not buff(s3)
        `s4
        `s1, cancel
        `s2, x>2
        """
    conf['coabs'] = ['Curran','Summer_Patia','Ieyasu']
    conf['share'] = ['Curran']
    conf['afflict_res.poison'] = 0

    def prerun(self):
        self.set_hp(80)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
