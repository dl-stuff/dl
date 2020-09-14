from core.advbase import *

def module():
    return Hanabusa

class Hanabusa(Adv):
    conf = {}
    conf['acl'] = """
        `dragon
        `s3, not buff(s3)
        `s1
        `s2
        `s4, x=5
        """
    conf['coabs'] = ['Halloween_Elisanne','Lucretia','Peony']
    conf['share'] = ['Summer_Patia']

    def prerun(self):
        self.s1_stance = EffectBuff('dance_of_blades', 0, lambda: None, self.stance_end)

    def s1_proc(self, e):
        if e.group == 0:
            self.s1_stance.on(20)
        elif e.group == 1:
            self.s1_stance.on(15)
        elif e.group == 2:
            self.stance_end()

    def s2_before(self, e):
        self.s2_bt_mod = Modifier('s2_bt', 'buff', 'time', 0.20*self.current_s['s1']).on()

    def s2_proc(self, e):
        self.s2_bt_mod.off()

    def stance_end(self):
        self.current_s['s1'] = 0

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)