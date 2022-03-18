from core.advbase import *
from module.template import Adv_INFUTP


class Gala_Zethia(Adv):
    DISABLE_DACL = True

    def prerun(self):
        # crit amp x5 x9
        self.buff1868 = 1
        # s1 sp slowdown
        self.s1sp = 0
        self.s1.autocharge_init(self.s1_autocharge).on()
        # bahamut
        self._servant_actions = {name: ServantAction(name, conf, self) for name, conf in self.conf.dservant.items()}
        Event("dragondrive").listener(self.start_servant)
        Event("dragondrive_end").listener(self.stop_servant)
        # bahamut will do x1 fs or fs spam sometimes, but it's random and not controllable
        self.sact_seq = ("x1", "x2", "x3", "x4")
        self.st_bahamut = 0
        self.c_servant_act = None

    @property
    def skills(self):
        return (self.s1, self.s3, self.s4)

    def s1_autocharge(self, t):
        s1_sp = 34000 * (3 - self.s1sp)
        log("sp", "s1_autocharge", s1_sp)
        self.s1.charge(s1_sp)

    def next_servant_action(self, prev):
        if not self.in_drg:
            return
        if self.st_bahamut >= 16:
            nact = "s1"
            self.st_bahamut = 0
        else:
            try:
                nact = self.sact_seq[self.sact_seq.index(prev.name) + 1]
            except (ValueError, IndexError):
                nact = self.sact_seq[0]
        self._servant_actions[nact].run()

    def start_servant(self, _=None):
        self._servant_actions["dshift"].run()

    def stop_servant(self, _=None):
        self.st_bahamut = 0
        if self.c_servant_act is not None:
            self.c_servant_act.stop()


class ServantAction:
    def __init__(self, name, conf, adv: Gala_Zethia) -> None:
        self.name = name
        self.conf = conf
        self.adv = adv
        self.startup_timer = Timer(self._cb_startup)
        self.recovery_timer = Timer(self._cb_recovery)

        self.act_event = Event(f"servant_{name}")
        self.act_event.name = f"{name}_bahamut"
        self.act_event.base = self.name
        self.act_event.group = "servant"
        self.act_event.dtype = "fs" if name == "fs" else name[0]
        self.act_event.index = 0

        self.cast = "x" if self.act_event.dtype == "x" else "cast"

    def run(self):
        startup = self.conf.startup / self.adv.speed()
        if self.conf["charge"]:
            startup += self.conf["charge"] / self.adv.c_speed()
        self.startup_timer.on(startup)
        self.adv.c_servant_act = self
        if self.name == "s1":
            # bahamut skill pauses the timer
            self.adv.dragonform.shift_end_timer.pause()

    def _cb_startup(self, t):
        if self.name != "dshift":
            log(self.cast, self.act_event.name)
        self.adv.schedule_hits(self.act_event, self.conf)
        recovery = self.conf.recovery / self.adv.speed()
        self.recovery_timer.on(recovery)

    def _cb_recovery(self, t):
        self.adv.next_servant_action(self)
        self.c_servant_act = None
        if self.name == "s1":
            # bahamut skill pauses the timer
            self.adv.dragonform.shift_end_timer.resume()

    def stop(self):
        self.recovery_timer.off()


class Gala_Zethia_INFUTP(Gala_Zethia, Adv_INFUTP):
    pass


variants = {None: Gala_Zethia, "INFUTP": Gala_Zethia_INFUTP}
