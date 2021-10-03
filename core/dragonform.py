import operator
from core.advbase import Dodge, Shift, Action, S
from core.timeline import Event, Listener, Timer, now
from core.log import log, g_logs
from core.acl import allow_acl, CONTINUE
from conf import DRG


class DragonForm:
    def __init__(self, name, conf, adv, dragon):
        self.name = name
        self.conf = conf
        self.adv = adv
        self.dragon = dragon

        # merge confs into adv conf
        self.dx_max = 0
        for dx, dxconf in self.conf.find(r"^dx\d+$"):
            # maybe parse this properly later
            dxconf.interrupt.s = 0
            dxconf.interrupt.dodge = 0
            dxconf.cancel.s = 0
            dxconf.cancel.dodge = 0
            adv.conf[dx] = dxconf
            self.dx_max = max(self.dx_max, int(dx[2:]))
        self.default_ds_x = self.conf["default_ds_x"] or self.dx_max  # the default combo idx to try dragon skill on
        self.default_x_loop = self.conf["default_x_loop"] or self.dx_max  # the default combo idx to end combo on
        for fs, fsconf in self.conf.find(r"^dfs\d*(_[A-Za-z0-9]+)?$"):
            adv.conf[fs] = fsconf
        self.ds_final = None
        for ds, dsconf in self.conf.find(r"^ds\d*(_[A-Za-z0-9]+)?$"):
            adv.conf[ds] = dsconf
            # rebind ds(1|2)_(before|proc)
            # delicious squid ink spaget
            ds_base = ds.split("_")[0]
            for sfn in ("before", "proc"):
                self.adv.rebind_function(self.dragon, f"{ds_base}_{sfn}", f"{ds_base}_{sfn}", overwrite=False)
            if ds.startswith("ds99") or dsconf.get("final"):
                self.ds_final = ds.split("_")[0]
        # make separate dodge action, may want to handle forward/backward later
        self.d_dodge = Dodge("dodge", self.conf.dodge)
        self.d_shift = Shift("dshift", name, self.conf.dshift)
        self.d_end = Shift("dend", name, self.conf.dend)

        # events
        self.status = False
        self.disabled_reasons = set()
        self.shift_event = Event("dragon")
        self.end_event = Event("dragon_end")
        self.shift_end_timer = Timer(self.d_shift_end)
        self.shift_silence_timer = Timer(None, 10)
        self.can_end = True
        Event("dshift").listener(self.d_shift_start, order=0)
        self.l_s = Listener("s", self.l_ds_pause, order=0)
        self.l_s_end = Listener("s_end", self.l_ds_resume, order=0)
        self.l_s_final_end = Listener("s_end", self.d_shift_end, order=1)
        self.l_s.off()
        self.l_s_end.off()
        self.l_s_final_end.off()

        self.allow_end_cd = self.conf.allow_end + self.dstime()

        # mods
        self.dracolith_mod = self.adv.Modifier("dracolith", "ex", "dragon", 0)
        self.dracolith_mod.get = self.ddamage
        self.dracolith_mod.off()
        self.shift_mods = [self.dracolith_mod]
        self.shift_spd_mod = None
        self.off_ele = self.adv.slots.c.ele != self.conf.d.ele
        self.previous_x = "default"

        # gauge
        self.dragon_gauge_val = self.conf.gauge_val
        self.conf.gauge_iv = min(int(self.adv.duration / 12), 15)
        self.dragon_gauge_timer = Timer(self.auto_gauge, timeout=max(1, self.conf.gauge_iv), repeat=1).on()
        self.dragon_gauge_pause_timer = None
        self.dragon_gauge_timer_diff = 0

        self.dragon_gauge = 0
        self.max_gauge = 1000
        self.shift_cost = 500

        # dragonbattle
        self.is_dragonbattle = False

    def get(self):
        return self.status

    @property
    def shift_silence(self):
        return bool(self.shift_silence_timer.online)

    def set_disabled(self, reason):
        if self.disabled_reasons is not None:
            self.disabled_reasons.add(reason)

    def unset_disabled(self, reason):
        if self.disabled_reasons is not None:
            self.disabled_reasons.discard(reason)

    @property
    def disabled(self):
        return bool(self.disabled_reasons)

    def set_dacts_enabled(self, enabled):
        for xact in self.adv.a_x_dict[DRG].values():
            xact.enabled = enabled
        fsact = self.adv.a_fs_dict.get(DRG)
        if fsact:
            fsact.set_enabled(enabled)
        for skey in ("ds1", "ds2"):
            self.adv.a_s_dict[skey].set_enabled(enabled)

    def auto_dodge(self, index=None):
        index = index or self.dx_max
        d_combo = self.adv.a_x_dict[DRG][index]
        if "dodge" not in d_combo.conf.cancel:
            return False
        dodge_t = d_combo.conf.cancel["dodge"] + self.d_dodge.getstartup() + self.d_dodge.getrecovery()
        if d_combo.conf.cancel["dx1"]:
            combo_t = d_combo.conf.cancel["dx1"] / d_combo.speed()
        else:
            combo_t = d_combo.getrecovery()
        return dodge_t < combo_t

    def dx_dodge_or_skill(self, index):
        # log("dx_dodge_or_skill", "x{}: c on {}, s on {}".format(index, self.default_ds_x, self.default_x_loop), self.adv.ds1.check())
        if index == self.default_ds_x and self.adv.ds1.check():
            return self.adv.ds1
        if index == self.default_x_loop:
            return self.d_dodge if self.auto_dodge(index=index) else False
        return False

    def pause_auto_gauge(self):
        if self.is_dragonbattle:
            return
        if self.dragon_gauge_pause_timer is None:
            self.dragon_gauge_timer_diff = self.dragon_gauge_timer.timing - now()
        else:
            self.dragon_gauge_timer_diff = self.dragon_gauge_pause_timer.timing - now()
        self.dragon_gauge_timer.off()

    def resume_auto_gauge(self, t):
        self.dragon_gauge_pause_timer = None
        self.auto_gauge(t)
        self.dragon_gauge_timer.on()

    def l_ds_pause(self, e):
        if self.status and e.base in ("ds1", "ds2"):
            self.shift_end_timer.pause()

    def l_ds_resume(self, e):
        if self.status and e.act.base in ("ds1", "ds2"):
            self.shift_end_timer.resume()

    @allow_acl
    def dtime(self):
        return self.conf.duration * self.adv.mod("dt") + self.conf.exhilaration * int(not self.off_ele)

    def dstime(self):
        try:
            return (self.conf.ds.startup + self.conf.ds.recovery) / self.d_shift.speed()
        except TypeError:
            return 0

    def reset_allow_end(self):
        self.allow_force_end_timer = Timer(None, timeout=self.allow_end_cd)
        self.allow_force_end_timer.on()
        self.allow_end_cd = min(self.allow_end_cd + self.conf.allow_end_step, self.dtime())

    @property
    def allow_end(self):
        return not bool(self.allow_force_end_timer.online)

    def dhaste(self):
        return self.adv.mod("dh", operator=operator.add)

    def _charge_dp(self, delta, reason):
        if delta == 0:
            return
        self.dragon_gauge += delta
        log(
            "dgauge",
            f"{int(delta):+}",
            f"{int(self.dragon_gauge)}/{int(self.max_gauge)} [{self.dragon_gauge//self.max_gauge}]",
            reason,
        )

    def auto_gauge(self, t):
        self.charge_gauge(self.dragon_gauge_val, percent=True, auto=True)

    def charge_gauge(self, value, utp=False, dhaste=True, percent=False, auto=False):
        dh = self.dhaste() if dhaste else 1
        if utp:
            dh *= self.adv.mod("utph", operator=operator.add)
        if percent:
            value *= self.max_gauge / 100
        value = self.adv.sp_convert(dh, value)
        delta = min(self.dragon_gauge + value, self.max_gauge) - self.dragon_gauge
        if delta != 0:
            self.dragon_gauge += delta
            log(
                "dragon_gauge",
                "{:+} ({:+.2f}%)".format(int(delta), delta / self.max_gauge * 100),
                f"{int(self.dragon_gauge)}/{int(self.max_gauge)}",
                "{:.2f}%".format(self.dragon_gauge / self.max_gauge * 100),
                "auto" if auto else "",
            )
        return value

    @allow_acl
    def ddamage(self):
        return self.conf.dracolith + self.adv.mod("da", operator=operator.add, initial=0)

    def d_shift_start(self, _=None):
        self.dragon_gauge -= self.shift_cost
        if self.off_ele:
            self.adv.element = self.adv.slots.d.ele
        if self.shift_spd_mod is not None:
            self.shift_spd_mod.on()
        self.pause_auto_gauge()
        for s in self.adv.dskills:
            s.reset_uses()
        self.adv.charge_p("dshift", 1.0, dragon_sp=True)
        self.previous_x = self.adv.current_x
        self.adv.current_x = DRG
        self.l_s.on()
        self.l_s_end.on()
        self.set_dacts_enabled(True)
        self.shift_end_timer.on(self.dtime())
        self.reset_allow_end()
        self.shift_event()

    def d_shift_end(self, e=None, reason="<timeout>"):
        if not self.status:
            return False
        doing = self.d_shift.getdoing()
        if self.ds_final and not self.l_s_final_end.get() and not (isinstance(doing, S) and doing.base[:2] == "ds"):
            self.l_s_final_end.on()
            ds_final = self.adv.a_s_dict[self.ds_final]
            ds_final.charged = self.adv.ds1.sp
            ds_final.reset_uses()
            ds_final()
            self.set_dacts_enabled(False)
            return False
        else:
            if self.off_ele:
                self.adv.element = self.adv.slots.c.ele
            if self.shift_spd_mod is not None:
                self.shift_spd_mod.off()
            self.shift_silence_timer.on()
            self.dragon_gauge_pause_timer = Timer(self.resume_auto_gauge).on(self.dragon_gauge_timer_diff)
            self.adv.current_x = self.previous_x
            self.l_s.off()
            self.l_s_end.off()
            self.l_s_final_end.off()
            self.set_dacts_enabled(False)
        self.end_event()
        self.d_end()
        g_logs.set_log_shift(end_reason=reason)
        self.status = False
        return True

    def d_shift_partial_end(self):
        if self.get():
            g_logs.set_log_shift(end_reason="<partial>")

    @allow_acl
    def check(self):
        if self.disabled_reasons or self.shift_silence:
            return False
        if self.dragon_gauge < self.shift_cost:
            return False
        if self.status:
            return False
        doing = self.d_shift.getdoing()
        if not doing.idle:
            if isinstance(doing, S):
                return False
        return True

    def shift(self):
        if not self.check():
            return False
        g_logs.set_log_shift(self.name)
        self.status = True
        return self.d_shift()

    def sack(self):
        if not self.status:
            return True
        if self.l_s_final_end.get():
            return False
        return self.allow_end and self.d_shift_end(reason="<forced>")


class DragonDrive(DragonForm):
    def __init__(self, name, conf, adv, dragon):
        super().__init__(name, conf, adv, dragon)
        self.model_type,
