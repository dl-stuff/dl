from core.advbase import *

echo_mod = 0.40
class Dragonyule_Lily(Adv):
    comment = 's1 overdamage team buff not considered'
    def prerun(self):
        self.starfall_strength = 0

    def fs_dragonyulelily_proc(self, e):
        self.starfall_strength = min(3, self.starfall_strength+1)

    def s2_proc(self, e):
        self.starfall_strength = 0

    def post_run(self, end):
        try:
            average_echo_att = self.sum_echo_att / g_logs.counts['s']['s1']
            self.comment += f'; {average_echo_att:.2f} avg overdamage att'
        except (KeyError, AttributeError):
            pass

variants = {None: Dragonyule_Lily}
