from module.template import RngCritAdv

class Eugene(RngCritAdv):
    def prerun(self):
        self.checkmate = 0
        o_s2_check = self.a_s_dict['s2'].check
        self.a_s_dict['s2'].check = lambda: not self.a_s_dict['s2']._static.silence and self.checkmate > 0
        self.config_rngcrit(cd=10)

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.checkmate = 0

    def rngcrit_skip(self):
        return self.inspiration()>=5

    def rngcrit_cb(self):
        self.inspiration.add(1)

    def s1_proc(self, e):
        if e.group == 2:
            self.checkmate = min(self.checkmate+1, 2)

    def s2_proc(self, e):
        self.checkmate -= 1

variants = {
    None: Eugene,
    'mass': Eugene
}
