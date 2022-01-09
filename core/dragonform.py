import operator
from core.advbase import Dodge, Shift, Action, S
from core.timeline import Event, Listener, Timer, now
from core.log import log, g_logs
from core.acl import allow_acl, CONTINUE
from core.modifier import Modifier
from conf import DRG, DEFAULT, DDRIVE, float_ceil


class DragonForm:
    def __init__(self, name, conf, adv, dragon, dform_mode=-1, unique_dform=False):
        self.name = name
        self.conf = conf
        self.adv = adv
        self.dragon = dragon
        self.dform_mode = dform_mode
        self.unique_dform = unique_dform

        self.shift_start_proc = None
        self.shift_end_proc = None
        self.config_actions()
        # events
        self.status = False
        self.disabled_reasons = set()
        self.dp_event = Event("dp")
        self.shift_end_timer = Timer(self.d_shift_end)
        self.shift_silence_timer = Timer(None, 10)
        self.can_end = True
        self.l_shift = Listener("dshift", self.d_shift_start, order=2)
        self.l_s = Listener("s", self.l_ds_pause, order=0)
        self.l_s_end = Listener("s_end", self.l_ds_resume, order=0)
        self.l_s_final_end = Listener("s_end", self.d_shift_end, order=0)
        self.l_act_end = Listener("act_end", self.d_shift_end, order=0)
        self.l_s.off()
        self.l_s_end.off()
        self.l_s_final_end.off()
        self.l_act_end.off()
        self.shift_skills = ("ds1", "ds2")

        self.allow_end_cd = self.conf.allow_end + self.dstime()
        self.shift_end_reason = None

        # mods
        self.dracolith_mod = Modifier("ex", "dragon", 1, get=self.ddamage)
        self.dracolith_mod.off()
        self.shift_mods = [self.dracolith_mod]
        self.shift_spd_mod = None
        self.off_ele = self.adv.slots.c.ele != self.conf.d.ele

        # gauge
        self.auto_gauge_val = 0.1  # percent
        self.auto_gauge_iv = min(int(self.adv.duration / 12), 15)
        self.dragon_gauge_timer = Timer(self.auto_gauge, timeout=max(1, self.auto_gauge_iv), repeat=1).on()
        self.dragon_gauge_pause_timer = None
        self.dragon_gauge_timer_diff = 0

        self.dragon_gauge = 0
        self.max_dragon_gauge = 1000
        self._shift_cost = 500
        self.shift_req = 500
        self.log_utp = False

        # dragonbattle
        self.is_dragonbattle = False

        # untimed shift
        self.untimed_shift = False

    @property
    def shift_cost(self):
        return float_ceil(self._shift_cost, Modifier.SELF.mod("dpcost", operator=operator.add))

    def set_dragonbattle(self):
        self.is_dragonbattle = True
        if self.dform_mode == 0:  # ddrive chara cant do dragon battle
            self.adv.stop()
            return
        for skey in self.shift_skills:
            self.adv.a_s_dict[skey].dragonbattle_skill = True
        self.dragon_gauge += max(self.shift_cost, self.shift_req)
        g_logs.log_dact_as_act = True

    def config_actions(self):
        # merge confs into adv conf
        self.dx_max = 0
        for dx, dxconf in self.conf.find(r"^dx\d+$"):
            self.adv.conf[dx] = dxconf
            self.dx_max = max(self.dx_max, int(dx[2:]))
        self.default_x_loop = self.conf["default_x_loop"] or self.dx_max  # the default combo idx to end combo on
        for fs, fsconf in self.conf.find(r"^dfs\d*(_[A-Za-z0-9]+)?$"):
            self.adv.conf[fs] = fsconf
            if not self.unique_dform:
                for sfn in ("before", "proc"):
                    self.adv.rebind_function(self.dragon, f"{fs}_{sfn}", f"{fs}_{sfn}", overwrite=False)
        self.ds_final = None
        for ds, dsconf in self.conf.find(r"^ds\d*(_[A-Za-z0-9]+)?$"):
            self.adv.conf[ds] = dsconf
            ds_base = ds.split("_")[0]
            if not self.unique_dform:
                for sfn in ("before", "proc"):
                    self.adv.rebind_function(self.dragon, f"{ds_base}_{sfn}", f"{ds_base}_{sfn}", overwrite=False)
            if ds.startswith("ds99") or dsconf.get("final"):
                self.ds_final = ds.split("_")[0]
        # make separate dodge action, may want to handle forward/backward later
        self.d_dodge = Dodge("dodge", self.conf.dodge)
        self.d_shift = Shift("dshift", self.name, self.conf.dshift)
        self.d_shift.is_dragon = True
        self.d_end = Shift("dend", self.name, self.conf.dend)

        self.shift_event = Event("dragon")
        self.end_event = Event("dragon_end")

        if self.dform_mode == -1:
            try:
                self.shift_start_proc = self.dragon.shift_start_proc
            except AttributeError:
                pass
            try:
                self.shift_end_proc = self.dragon.shift_end_proc
            except AttributeError:
                pass

    def in_dform(self):
        return self.status

    def in_ddrive(self):
        return False

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
        for fsn, fsact in self.adv.a_fs_dict.items():
            if fsn.startswith("dfs"):
                fsact.set_enabled(enabled)
        for skey in self.shift_skills:
            self.adv.a_s_dict[skey].set_enabled(enabled)

    def auto_dodge(self, index=None):
        index = index or self.dx_max
        d_combo = self.adv.a_x_dict[DRG][index]
        if "dodge" not in d_combo.conf.cancel:
            return False
        dodge_t = d_combo.conf.cancel["dodge"] + self.d_dodge.getstartup() + self.d_dodge.getrecovery()
        if d_combo.conf.cancel["dx1"]:
            combo_t = d_combo.conf.cancel["dx1"] / d_combo.speed()
        elif d_combo.conf.cancel["any"]:
            combo_t = d_combo.conf.cancel["any"] / d_combo.speed()
        else:
            combo_t = d_combo.getrecovery()
        return dodge_t < combo_t

    def dx_dodge_or_wait(self, index):
        # log("dx_dodge_or_skill", "x{}: c on {}, s on {}".format(index, self.default_ds_x, self.default_x_loop), self.adv.ds1.check())
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
        if self.status and not self.untimed_shift and e.base in self.shift_skills:
            self.shift_end_timer.pause()
            log("shift_end_timer", "pause", self.shift_end_timer.timing, self.shift_end_timer.pause_time)

    def l_ds_resume(self, e):
        if self.status and not self.untimed_shift and e.act.base in self.shift_skills:
            self.shift_end_timer.resume()
            log("shift_end_timer", "resume", self.shift_end_timer.timing, self.shift_end_timer.timing - now())

    @allow_acl
    def dtime(self):
        return self.conf.duration * Modifier.SELF.mod("dt") + self.conf.exhilaration * int(not self.off_ele)

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
        return Modifier.SELF.mod("dph", operator=operator.add)

    def _charge_dp(self, name, value):
        gauge_before = self.dragon_gauge
        self.dragon_gauge = max(0, min(self.max_dragon_gauge, self.dragon_gauge + value))
        delta = self.dragon_gauge - gauge_before
        if delta != 0 and not self.log_utp:
            log(
                "dgauge",
                name,
                f"{int(delta):+}",
                f"{int(self.dragon_gauge)}/{int(self.max_dragon_gauge)} [{self.dragon_gauge//self.shift_cost}]",
            )
        self.dp_event.name = name
        self.dp_event.value = value
        self.dp_event.delta = delta
        self.dp_event.gauge = self.dragon_gauge
        self.dp_event()
        return value

    def charge_dprep(self, value):
        return self._charge_dp("dprep", float_ceil(self.max_dragon_gauge, value))

    def charge_dp(self, name, value):
        return self._charge_dp(name, float_ceil(value, self.dhaste()))

    def auto_gauge(self, t):
        self._charge_dp("auto", float_ceil(self.max_dragon_gauge * self.auto_gauge_val, self.dhaste()))

    @allow_acl
    def ddamage(self):
        return self.conf.dracolith + Modifier.SELF.mod("dragondmg", operator=operator.add, initial=0)

    def extend_shift_time(self, value, percent=True):
        max_d = self.dtime()
        cur_d = self.shift_end_timer.timeleft()
        delta_t = value
        if percent:
            delta_t *= self.conf.duration
        delta_t = min(max_d, cur_d + delta_t) - cur_d
        log("shift_time", f"{delta_t:+2.4}", f"{cur_d+delta_t:2.4}")
        if cur_d + delta_t > 0.001:
            self.shift_end_timer.add(delta_t)
        else:
            self.shift_end_timer.off()
            doing = self.d_shift.getdoing()
            if isinstance(doing, S):
                self.l_act_end.on()
            else:
                self.shift_end_timer.on(0.00001)
            self.set_dacts_enabled(False)

    def d_shift_start(self, _=None):
        self.status = True
        self.dragon_gauge -= self.shift_cost
        g_logs.set_log_shift(shift_name=self.name)
        if self.shift_start_proc:
            self.shift_start_proc()
        if self.off_ele:
            self.adv.element = self.adv.slots.d.ele
        if self.shift_spd_mod is not None:
            self.shift_spd_mod.on()
        self.pause_auto_gauge()
        for s in self.adv.dskills:
            s.reset_uses()
        self.adv.set_dacl(True)
        self.l_s.on()
        self.l_s_end.on()
        self.set_dacts_enabled(True)
        self.adv.charge_p("dshift", 1.0, dragon_sp=True)
        if self.untimed_shift:
            self.shift_end_timer.on(self.dtime() / (1 + self.adv.sub_mod("dt", "getrektoof")))
            self.shift_end_timer.pause()
        else:
            log("shift_end_timer", "on", self.dtime())
            self.shift_end_timer.on(self.dtime())
        self.reset_allow_end()
        self.shift_event()

    def d_shift_end(self, e=None, reason="timeout"):
        if not self.status or self.is_dragonbattle:
            return False
        doing = self.d_shift.getdoing()
        if self.ds_final and not (isinstance(doing, S) and doing.base in self.shift_skills) and not self.l_s_final_end.get():
            ds_final = self.adv.a_s_dict[self.ds_final]
            if ds_final.ac.conf.final and ds_final.ac.enabled:
                self.shift_end_reason = reason
                self.l_s_final_end.on()
                ds_final.reset_uses()
                ds_final.charged = ds_final.sp
                ds_final()
                self.set_dacts_enabled(False)
                return False

        if self.off_ele:
            self.adv.element = self.adv.slots.c.ele
        if self.shift_spd_mod is not None:
            self.shift_spd_mod.off()
        self.shift_silence_timer.on()
        if self.dragon_gauge_timer_diff > 0:
            self.dragon_gauge_pause_timer = Timer(self.resume_auto_gauge).on(self.dragon_gauge_timer_diff)
        self.l_s.off()
        self.l_s_end.off()
        self.l_s_final_end.off()
        self.l_act_end.off()
        self.set_dacts_enabled(False)
        self.adv.set_dacl(False)
        log("d_shift_end", self.end_event.name, self.adv.def_mod())
        self.end_event()
        self.d_end()
        self.status = False
        g_logs.set_log_shift(end_reason=self.shift_end_reason or reason)
        self.shift_end_reason = None
        if self.shift_end_proc:
            self.shift_end_proc()
        return True

    def d_shift_partial_end(self):
        if self.status and abs(self.dform_mode) == 1:
            g_logs.set_log_shift(end_reason="partial")

    @allow_acl
    def check(self):
        if self.disabled_reasons or self.shift_silence:
            return False
        if self.dragon_gauge < max(self.shift_cost, self.shift_req):
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
        return self.d_shift()

    def sack(self):
        if self.status and not (self.l_s_final_end.get() or self.l_act_end.get()) and self.allow_end:
            self.d_shift_end(reason="forced")
            self.shift_end_timer.off()
            return True
        return False


class DragonFormUTP(DragonForm):
    def __init__(self, name, conf, adv, dragon):
        utp_params = adv.conf.c.utp
        # dform_modes
        # 0: ddrive as adventurer
        # 1: ddrive as dragon
        # 2: ddrive as adventurer, with servant
        super().__init__(name, conf, adv, dragon, dform_mode=utp_params[0], unique_dform=True)
        self.shift_mods = []
        self._shift_cost = 0
        self.shift_req = 0
        self.utp_gauge = 0
        self.ds_final = None

        self.max_utp_gauge = utp_params[1]
        self.utp_shift_req = utp_params[2]
        self.utp_drain = utp_params[3]
        self.utp_infinte = False
        self.utp_event = Event("utp")
        self.log_utp = True

        if self.dform_mode == 1:
            g_logs.log_dact_as_act = True
            for ds in self.shift_skills:
                try:
                    del self.adv.conf[ds]["uses"]
                except KeyError:
                    pass
        else:
            self.ddrive_fs_list = [fsn for fsn, _ in self.adv.conf.find(f"^fs\d*_{DDRIVE}$")]
            self.shift_skills = [sn.split("_")[0] for sn, _ in self.adv.conf.find(f"^s\d*_{DDRIVE}$")]
            self.l_ddrive_end = Listener("act_end", self.d_dragondrive_end, order=0)
            self.l_ddrive_end.off()
            self.ddrive_end_reason = None

    def in_dform(self):
        return self.dform_mode == 1 and self.status

    def in_ddrive(self):
        return self.status

    def set_utp_infinite(self):
        self.utp_infinte = True
        self.utp_gauge = self.max_utp_gauge

    def utphaste(self):
        return self.dhaste() + Modifier.SELF.mod("utph", operator=operator.add, initial=0)

    def _charge_utp(self, name, value):
        # sync with timer value
        if self.utp_infinte:
            self.utp_gauge = self.max_utp_gauge
        elif self.status:
            self.utp_gauge = self.shift_end_timer.timeleft() * self.utp_drain
        gauge_before = self.utp_gauge
        # use utp_gauge from here on
        self.utp_gauge = max(0, min(self.max_utp_gauge, gauge_before + value))
        delta = self.utp_gauge - gauge_before
        if delta != 0:
            if self.log_utp:
                log(
                    "utpgauge",
                    name,
                    f"{int(delta):+} ({delta/self.utp_drain:+2.4}s)",
                    f"{int(self.utp_gauge)}/{int(self.max_utp_gauge)} ({self.dtime():2.4}s)",
                )
            if self.utp_gauge <= 0:
                self.utp_gauge = 0
                self.d_shift_end(reason="gauge deplete")
            else:
                self.shift_end_timer.add(delta / self.utp_drain)
        self.utp_event.name = name
        self.utp_event.value = value
        self.utp_event.delta = delta
        self.utp_event.gauge = self.utp_gauge
        self.utp_event()
        return value

    def charge_dprep(self, value):
        super().charge_dprep(value)
        return self._charge_utp("dprep", float_ceil(self.max_utp_gauge, value / 100))

    def charge_dp(self, name, value):
        return self._charge_utp(name, super().charge_dp(name, value))

    def charge_utp(self, name, value):
        if value > 0:
            value = float_ceil(value, self.utphaste())
        return self._charge_utp(name, value)

    def charge_utprep(self, name, value):
        return self._charge_utp(name, float_ceil(self.max_utp_gauge, value / 100))

    def auto_gauge(self, t):
        super().auto_gauge(t)
        self._charge_utp("auto", float_ceil(self.max_dragon_gauge * self.auto_gauge_val, self.utphaste()))

    def config_actions(self):
        if self.dform_mode == 1:
            super().config_actions()
            self.shift_event = Event("divinedragon")
            self.end_event = Event("divinedragon_end")
            return
        # should maybe take the actual shift action from the modes
        self.name = "Dragondrive"
        self.d_shift = Shift("dshift", self.name, self.conf.dshift)
        self.shift_event = Event("dragondrive")
        self.end_event = Event("dragondrive_end")

    def set_dacts_enabled(self, enabled):
        if self.dform_mode == 1:
            return super().set_dacts_enabled(enabled)
        # ddrive
        try:
            for _, xact in self.adv.a_x_dict[DDRIVE].items():
                xact.enabled = enabled
            if enabled:
                self.adv.current.set_action("x", DDRIVE)
            else:
                self.adv.current.unset_action("x", DDRIVE)
        except KeyError:
            pass
        if self.ddrive_fs_list:
            for fsn in self.ddrive_fs_list:
                self.adv.a_fs_dict[fsn].set_enabled(enabled)
            if enabled:
                self.adv.current.set_action("fs", DDRIVE)
            else:
                self.adv.current.unset_action("fs", DDRIVE)
        if self.shift_skills:
            for sn in self.shift_skills:
                if DDRIVE in self.adv.a_s_dict[sn].act_dict:
                    if enabled:
                        self.adv.current.set_action(sn, DDRIVE)
                    else:
                        self.adv.current.unset_action(sn, DDRIVE)

    def dtime(self):
        return self.utp_gauge / self.utp_drain

    @allow_acl
    def check(self):
        if self.utp_gauge < self.utp_shift_req:
            return False
        return super().check()

    def d_dragondrive_start(self):
        self.status = True
        self.set_dacts_enabled(True)
        self.adv.set_dacl(True)
        self.l_s.on()
        self.l_s_end.on()
        self.l_ddrive_end.on()
        self.shift_end_timer.on(self.dtime())
        self.shift_event()
        log("dragondrive", "start", self.dtime())

    def d_shift_start(self, _=None):
        if self.dform_mode == 1:
            super().d_shift_start()
        else:
            self.d_dragondrive_start()
        if self.utp_infinte:
            self.shift_end_timer.off()
            self.l_s.off()
            self.l_s_end.off()

    def d_dragondrive_end(self, _=None):
        if self.ddrive_end_reason is not None:
            self.l_s.off()
            self.l_s_end.off()
            self.l_ddrive_end.off()
            self.shift_silence_timer.on()
            self.set_dacts_enabled(False)
            self.adv.set_dacl(False)
            self.status = False
            log("dragondrive", "end", self.ddrive_end_reason)
            self.end_event()
            self.ddrive_end_reason = None
            return True
        return False

    @property
    def allow_end(self):
        return True

    def pause_auto_gauge(self):
        pass

    def reset_allow_end(self):
        pass

    def d_shift_end(self, e=None, reason="timeout"):
        if not self.status:
            return False
        if reason == "timeout":
            self.utp_gauge = 0
        if self.dform_mode == 1:
            return super().d_shift_end(e=e, reason=reason)
        self.ddrive_end_reason = reason
        return False
