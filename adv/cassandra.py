from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Cassandra

class Cassandra(Adv):
    a3 = [('prep',1.00), ('scharge_all', 0.05)]
    a3 = ('ro', 0.15, 180)

    conf = {}
    conf['slots.a'] = Candy_Couriers()+Primal_Crisis()
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = """
        `dragon(c3 s end), x=5
        `s3, not self.s3_buff
        `s4
        `s1, cancel
        `s2, x>2
        """
    conf['coabs'] = ['Curran','Summer_Patia','Ieyasu']
    conf['share'] = ['Curran']
    conf['afflict_res.poison'] = 0

    def prerun(self):
        self.set_hp(80)

    def s1_proc(self, e):
        self.afflics.poison(e.name,120,0.582)
        self.buff_max_hp(f'{e.name}_hp', 0.05)

    def s2_proc(self, e):
        with CrisisModifier(e.name, 1, self.hp):
            self.dmg_make(e.name,9.72)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
