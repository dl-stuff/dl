from core.advbase import *


class Yoshitsune(Adv):
    comment = "no counter on s1/dodge"

    def prerun(self):
        Event("dodge").listener(self.l_dodge_attack, order=0)
        self.a1_cd = True

    def a1_cd_end(self, _):
        self.a1_cd = False

    def l_dodge_attack(self, e):
        log("cast", "dodge_attack")
        for _ in range(7):
            self.add_combo("dodge")
            self.dmg_make("dodge", 0.10)
        if not self.a1_cd:
            self.a1_cd = True
            Timer(self.a1_cd_end).on(4.999)
            self.hitattr_make("dodge", "dodge", "default", 0, self.conf.dodge.attr_spd)


class Yoshitsune_COUNTER(Yoshitsune):
    comment = "always counter on s1/dodge"

    def prerun(self):
        super().prerun()
        self.a1_cd = False
        self.conf.s1.attr = self.conf.s1.attr_counter


variants = {None: Yoshitsune, "COUNTER": Yoshitsune_COUNTER}
