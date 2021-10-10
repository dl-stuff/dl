from core.advbase import *


class Aether(Skill):
    def __init__(self, name=None, acts=None, true_sp=1, maxcharge=3):
        super().__init__(name=name, acts=acts)
        self.maxcharge = maxcharge
        self.true_sp = true_sp

    @property
    def ac(self):
        if self.flames == 3 and self.count == 3:
            return self.act_dict["awakening"]
        return self.act_dict[self._static.current_s[self.name]]

    @property
    def real_sp(self):
        return self.true_sp

    def check(self):
        return self.flames and super().check()

    def cast(self):
        self.charged -= self.ac.conf.sp
        self._static.s_prev = self.name
        self.silence_end_timer.on(self.silence_duration)
        self._static.silence = 1
        if self.ac.uses > 0:
            self.ac.uses -= 1
        if loglevel >= 2:
            log("silence", "start")
        return 1


class Chrom(Adv):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.a_s_dict["s2"] = Aether("s2", true_sp=self.conf.s2.sp, maxcharge=3)
        self.a_s_dict["s2"].flames = 0

    @property
    def flames(self):
        return self.s2.flames

    def s1_proc(self, e):
        # get fucked
        if self.nihilism:
            return
        if self.s2.flames < 3:
            self.s2.flames += 1

    def s2_proc(self, e):
        self.s2.flames = 0


variants = {None: Chrom}
