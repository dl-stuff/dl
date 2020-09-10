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
        self.phase['s1'] = 0
        self.s1_stance = EffectBuff('dance_of_blades', 0, lambda: None, self.stance_end)

    def s1_proc(self, e):
        if self.phase['s1'] == 0:
            self.conf.s1.sp = 2567
            self.phase['s1'] = 1
            self.s1_stance.on(20)
        elif self.phase['s1'] == 1:
            self.dmg_make(e.name,1.94)
            self.phase['s1'] = 2
            self.s1_stance.on(15)
        elif self.phase['s1'] == 2:
            self.dmg_make(e.name,2.51)
            self.stance_end()

    def s2_proc(self, e):
        if self.phase['s1'] == 0:
            Teambuff(e.name,0.15,15).on()
        elif self.phase['s1'] == 1:
            Teambuff(e.name,0.15,18).on()
        elif self.phase['s1'] == 2:
            Teambuff(e.name,0.15,21).on()

    def stance_end(self):
        self.conf.s1.sp = 2840
        self.phase['s1'] = 0

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)