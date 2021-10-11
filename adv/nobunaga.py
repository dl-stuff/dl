from core.advbase import *


class Nobunaga(Adv):
    def build_rates(self, as_list=True):
        rates = super().build_rates(as_list=False)
        if self.burning_ambition > 0:
            rates["buffed"] = 1.00
        return rates if not as_list else list(rates.items())

    def prerun(self):
        self.burning_ambition = 0
        self.ba_t = Timer(self.ba_proc)
        self.ba_listener = Listener("dispel", self.ba_proc)

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.burning_ambition = 0
        adv.rebind_function(Nobunaga, "ba_proc")
        adv.ba_t = Timer(adv.ba_proc)
        adv.ba_listener = Listener("dispel", adv.ba_proc).off()

    def s1_proc(self, e):
        if self.berserk_mode or self.burning_ambition:
            return
        self.burning_ambition = self.dmg_formula("s", 15.65)
        self.ba_t.name = e.name
        self.ba_t.on(30)
        self.ba_listener.on()

    def ba_proc(self, t):
        if self.burning_ambition > 0:
            self.dmg_make(f"{t.name}_burning_ambition", self.burning_ambition, fixed=True)
            self.burning_ambition = 0
            self.ba_t.off()
            self.ba_listener.off()
            return True
        return False


variants = {None: Nobunaga}
