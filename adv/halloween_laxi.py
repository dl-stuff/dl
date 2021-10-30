from core.advbase import *

MAX_CLOCKWORK_GAUGE = 1000000000


class Halloween_Laxi(Adv):
    def prerun(self):
        self.clockwork_timer = Timer(self.clockwork_off, 15.0)
        self.clockwork_listeners = (
            Listener("fs_start", lambda _: self.clockwork_timer.resume(), order=0),
            Listener("fs_end", lambda _: self.clockwork_timer.pause(), order=0),
        )
        self.clockwork_regen = Timer(self.clockwork_on, 10.0)
        self.clockwork_on()

        self.a3_edge_buffs = []
        self.a3_punish_buffs = []
        self.buff1990 = 0

    @property
    def clockwork(self):
        return self.a_fs_dict["fs"].enabled

    def clockwork_on(self, t=None):
        log("clockwork", "start")
        self.a_fs_dict["fs"].set_enabled(True)
        for lst in self.clockwork_listeners:
            lst.on()
        self.clockwork_timer.on()
        self.clockwork_timer.pause()

    def clockwork_off(self, t=None):
        log("clockwork", "timeout")
        self.a_fs_dict["fs"].set_enabled(False)
        for lst in self.clockwork_listeners:
            lst.off()
        self.clockwork_regen.on()

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None, dtype=None):
        if add_gauge := attr.get("cp", 0):
            log("clockwork", "add", add_gauge)
            if self.clockwork:
                delta = add_gauge * 15 / MAX_CLOCKWORK_GAUGE
                cur_d = self.clockwork_timer.timeleft()
                delta = min(15.0, cur_d + delta) - cur_d
                self.clockwork_timer.add(delta)
            else:
                delta = add_gauge * 10.0 / MAX_CLOCKWORK_GAUGE
                if self.clockwork_regen.add(-delta) <= 0:
                    self.clockwork_on()
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit, dtype=dtype)

    def add_combo(self, name="#"):
        result = super().add_combo(name)
        if not result:
            for buff in itertools.chain(self.a3_edge_buffs, self.a3_punish_buffs):
                buff.off()
            self.a3_edge_buffs = []
            self.a3_punish_buffs = []
            self.buff1990 = 0
        if self.condition("always connect hits"):
            a_hits = self.hits // 15
            if len(self.a3_edge_buffs) < 3 and a_hits > len(self.a3_edge_buffs):
                self.a3_edge_buffs.append(Selfbuff("a3_edge", 0.25, -1, "edge", "flashburn").on())
                self.a3_punish_buffs.append(Selfbuff("a3_punisher", 0.25, -1, "flashburn_killer", "passive").on())
            self.buff1990 = min(4, self.hits // 25)
        return result


variants = {None: Halloween_Laxi}
