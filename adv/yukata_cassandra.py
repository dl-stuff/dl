from core.advbase import *
from module.template import LowerMCAdv


class Yukata_Cassandra(Adv):
    A3_VALUE = 0.35

    def prerun(self):
        self.a3_att_mod = Modifier("a3_att", "att", "passive", self.A3_VALUE, get=self.a3_get)

    def a3_get(self):
        return self.s2.sp == self.s2.charged


class Yukata_Cassandra_50MC(Yukata_Cassandra, LowerMCAdv):
    A3_VALUE = 0.30


variants = {None: Yukata_Cassandra, "50MC": Yukata_Cassandra_50MC}
