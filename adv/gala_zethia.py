from core.advbase import *
from module.template import InfiniteUTPAdv


class DodgeOnX(Dodge):
    def __init__(self, name, conf, act=None):
        super().__init__(name, conf, act=act)
        self.retain_x = None

    def _cb_acting(self, e):
        super()._cb_acting(e)
        if isinstance(self.getprev(), X):
            self.retain_x = self.getprev()

    def _cb_act_end(self, e):
        super()._cb_act_end(e)


class Gala_Zethia(Adv):
    DISABLE_DACL = True

    def prerun(self):
        # crit amp x5 x9
        self.buff1868 = 1
        # s1 sp slowdown
        self.s1sp = 0
        self.s1.autocharge_init(self.s1_autocharge).on()
        # dodge from x
        self.a_dodge_on_x = DodgeOnX("dodge", self.conf.dodge_on_x)
        # bahamut
        self._servant_actions = {name: ServantAction(name, conf, self) for name, conf in self.conf.dservant.items()}
        Event("dragondrive").listener(self.start_servant)
        Event("dragondrive_end").listener(self.stop_servant)
        # irl bahamut will randomly FS, not represented here
        self.sact_seq = ("x1", "x2", "x3", "x4")
        # this is likely meant to be reset on each shift irl, but it doesn't seem to happen
        self.st_bahamut = 0
        self.c_servant_act = None

    @property
    def skills(self):
        return (self.s1, self.s3, self.s4)

    def _next_x(self):
        doing = self.action.getdoing()
        if doing == self.action.nop:
            doing = self.action.getprev()
        if doing == self.a_dodge_on_x and doing.retain_x is not None:
            return super()._next_x(prev=doing.retain_x)
        return super()._next_x()

    @allow_acl
    def dodge(self):
        if isinstance(self.action.getdoing(), X):
            return self.a_dodge_on_x()
        return self.a_dodge()

    def s1_autocharge(self, t):
        s1_sp = 34000 * (3 - self.s1sp)
        log("sp", "s1_autocharge", s1_sp)
        self.s1.charge(s1_sp)

    def next_servant_action(self, prev):
        if not self.in_drg:
            return
        if self.st_bahamut >= 16:
            nact = "s1"
        else:
            try:
                nact = self.sact_seq[self.sact_seq.index(prev.name) + 1]
            except (ValueError, IndexError):
                nact = self.sact_seq[0]
        self._servant_actions[nact].run()

    def start_servant(self, _=None):
        self._servant_actions["dshift"].run()

    def stop_servant(self, _=None):
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

    def _cb_startup(self, t):
        if self.name != "dshift":
            log(self.cast, self.act_event.name)
        self.adv.schedule_hits(self.act_event, self.conf)
        recovery = self.conf.recovery / self.adv.speed()
        self.recovery_timer.on(recovery)

    def _cb_recovery(self, t):
        self.adv.next_servant_action(self)
        self.c_servant_act = None

    def stop(self):
        self.recovery_timer.off()


class Gala_Zethia_INFUTP(Gala_Zethia, InfiniteUTPAdv):
    pass


variants = {None: Gala_Zethia, "INFUTP": Gala_Zethia_INFUTP}
