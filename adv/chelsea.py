from core.advbase import *
def module():
    return Chelsea

class Chelsea(Adv):
    conf = {}
    conf['slots.d'] = 'Dreadking_Rathalos'
    conf['slots.a'] = ['Mega_Friends', 'Dear_Diary']
    conf['acl'] = """
        `s3,not buff(s3)
        `s2, fsc
        `s1, fsc and self.hp < 30 and buffstack(ro) < 3
        `s4, fsc
        `dodge, fsc
        `fs
    """
    conf['coabs'] = ['Blade', 'Grace', 'Hunter_Berserker']
    conf['share'] = ['Summer_Patia']

    def prerun(self):
        Event('dragon').listener(self.s2_clear)
        Event('s').listener(self.s_hp_check, order=0)
        self.s2_buffs = []

    def s2_clear(self, e):
        for b in self.s2_buffs:
            b.off()
        self.s2_buffs = []

    def fs_before(self, e):
        if self.obsession:
            self.add_hp(-3)

    def x_before(self, e):
        if self.obsession:
            self.add_hp(-3)

    def s_hp_check(self, e):
        if self.obsession and e.name in self.damage_sources:
            self.add_hp(-3)

    @property
    def obsession(self):
        return len(self.s2_buffs)

    def s2_proc(self, e):
        self.s2_buffs.append(Selfbuff('s2_obsession',0.3,60,'att','buff').on())

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)