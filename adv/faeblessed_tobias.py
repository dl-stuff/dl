from core.advbase import *
from conf import DEFAULT


class Faeblessed_TobiasXAlt(XAltBuff):
    def enable_x(self, enabled):
        super().enable_x(enabled)
        self.adv.a_fs_dict["fs"].set_enabled(not enabled)
        self.adv.a_dodge.enabled = not enabled


class Faeblessed_Tobias(Adv):
    def prerun(self):
        self.s2_x_alt = Faeblessed_TobiasXAlt(group="fae")
        Event("s").listener(self.interrupt_fae)

    def s2_proc(self, e):
        if e.group != "enhanced":
            self.s2_x_alt.on(10)

    def interrupt_fae(self, e):
        if e.name != "s1" and self.s2_x_alt.get():
            log("debug", "interrupt_fae", f"by {e.name}")
            self.s2_x_alt.off()
            self.current_s["s2"] = DEFAULT


variants = {None: Faeblessed_Tobias}
