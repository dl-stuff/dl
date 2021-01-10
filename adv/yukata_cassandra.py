from core.advbase import *

class Yukata_Cassandra(Adv):
    comment = 's1 overdamage team buff not considered'
    def prerun(self):
        self.a3_att_mod = Modifier('a3_att', 'att', 'passive', 0.30, get=self.a3_get)

    def a3_get(self):
        return self.s2.sp == self.s2.charged

    def post_run(self, end):
        try:
            average_echo_att = self.sum_echo_att / g_logs.counts['s']['s1']
            self.comment += f'; {average_echo_att:.2f} avg overdamage att'
        except KeyError:
            pass


variants = {None: Yukata_Cassandra}
