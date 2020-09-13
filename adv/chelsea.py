from core.advbase import *
from slot.d import *
from slot.a import *
def module():
    return Chelsea

class Chelsea(Adv):
    conf = {}
    conf['slots.d'] = Dreadking_Rathalos()
    conf['slots.a'] = Mega_Friends()+Primal_Crisis()
    conf['acl'] = """
        `s3, fsc and not buff(s3)
        `s1, fsc
        `s2, fsc
        `s4, fsc
        `fs, x=1
    """
    conf['coabs'] = ['Blade', 'Grace', 'Serena']
    conf['share'] = ['Summer_Patia']

    def prerun(self):
        Event('dragon').listener(self.s2_clear)
        self.s2_buffs = []
        Event('s').listener(self.s_hp_check, order=0)

    def s2_clear(self, e):
        for b in self.s2_buffs:
            b.off()
        self.s2_buffs = []

    def x_proc(self, e):
        if self.obsession:
            self.add_hp(-3)

    def s_hp_check(self, e):
        if self.obsession and e.name in self.damage_sources:
            self.add_hp(-3)

    def obsession(self):
        return len(self.s2_buffs)

    def s2_proc(self, e):
        self.s2_buffs.append(Selfbuff('s2_obsession',0.3,60).on())

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)