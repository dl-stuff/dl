from core.advbase import *


class Armored_Yachiyo(Adv):
    def prerun(self):
        if self.condition("unrelenting_blade"):
            Timer(self.unrelenting_blade).on(15)
            Timer(self.unrelenting_blade).on(30)
            Timer(self.unrelenting_blade).on(45)

    def unrelenting_blade(self, t):
        Modifier("a1_unrelenting_blade", "att", "passive", 0.2)


variants = {None: Armored_Yachiyo}
