from conf import DEFAULT
from core.advbase import *
from module.template import SigilAdv


class Basileus(SigilAdv):
    comment = "change mode by dodge"
    conf = {
        "acl": [
            "`s1",
            "`dodge, x=5",
        ]
    }

    def prerun(self):
        self.config_sigil(duration=300, x=True, s1=True, s2=True, fs=True)
        self.ranged_mode = ModeManager(group="ranged", x=True, s1=True, s2=True)
        self.l_hit = Listener("hit", self.combo_sigil_and_echo)
        self.a1_hit = 0
        self.a3_active_time = None

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.current_s[dst] = "sigil"

    @property
    def close_combat(self):
        return not self.ranged_combat

    @property
    def ranged_combat(self):
        return not self.unlocked and self.ranged_mode.get()

    def dodge_proc(self, e):
        log("dodge_proc")
        if not self.unlocked:
            if not self.ranged_combat:
                self.ranged_mode.on()
            else:
                self.ranged_mode.off()

    def combo_sigil_and_echo(self, e):
        if not self.unlocked:
            n_a1_hit = e.hits // 25
            if n_a1_hit > self.a1_hit and not self.is_set_cd("a1_sigil", 8):
                self.a_update_sigil(-15)
            self.a1_hit = n_a1_hit
        if self.echo == 1 and e.hits >= 15:
            self.a3_active_time = self.enable_echo("a3_echo", active_time=self.a3_active_time, mod=0.3)
        else:
            self.disable_echo("a3_echo", self.a3_active_time)


class Basileus_UNLOCKED(Basileus):
    SAVE_VARIANT = False

    def prerun(self):
        super().prerun()
        self.a_update_sigil(-300)


variants = {None: Basileus, "UNLOCKED": Basileus_UNLOCKED}
