import operator
from core.advbase import Dodge, Shift, S
from core.timeline import Event, Timer, now
from core.log import log, g_logs
from core.acl import allow_acl
from math import ceil

DFORM = "drg"


def _append_dform(act):
    parts = act.split("_", 1)
    parts[0] = parts[0][1:]
    if len(parts) == 1:
        return f"{parts[0]}_{DFORM}"
    else:
        return f"{parts[0]}_{parts[1]}{DFORM}"


class DragonForm:
    def __init__(self, name, conf, adv, dragon):
        self.name = name
        self.conf = conf
        self.adv = adv
        self.dragon = dragon

        # merge confs into adv conf
        for dx, dxconf in self.conf.find(r"^dx\d+$"):
            # maybe parse this properly later
            dxconf.interrupt.s = 0
            dxconf.interrupt.dodge = 0
            dxconf.cancel.s = 0
            dxconf.cancel.dodge = 0
            adv.conf[_append_dform(dx)] = dxconf
        for fs, fsconf in self.conf.find(r"^dfs\d*(_[A-Za-z0-9]+)?$"):
            adv.conf[_append_dform(fs)] = fsconf
        for ds, dsconf in self.conf.find(r"^ds\d*(_[A-Za-z0-9]+)?$"):
            adv.conf[ds] = dsconf
            # rebind ds(1|2)_(before|proc)
            # delicious squid ink spaget
            ds_base = ds.split("_")[0]
            for sfn in ("before", "proc"):
                self.adv.rebind_function(self.dragon, f"{ds_base}_{sfn}", f"{ds_base}_{sfn}", overwrite=False)
        # make separate dodge action, may want to handle forward/backward later
        self.d_dodge = Dodge("dodge", self.conf.dodge)
        self.d_shift = Shift("dshift", self.conf.dshift)

        # events
        self.status = False
        self.disabled_reasons = set()
        self.shift_event = Event("dragon")
        self.end_event = Event("dragon_end")
        self.ds_event = Event("ds")
        self.shift_end_timer = Timer(self.d_shift_end)
        self.shift_silence = False

        # mods
        self.dracolith_mod = self.adv.Modifier("dracolith", "ex", "dragon", 0)
        self.dracolith_mod.get = self.ddamage
        self.dracolith_mod.off()
        self.shift_mods = [self.dracolith_mod]
        self.shift_spd_mod = None
        self.off_ele = self.adv.slots.c.ele != self.conf.d.ele

        # gauge
        self.dragon_gauge = 0
        self.dragon_gauge_val = self.conf.gauge_val
        self.conf.gauge_iv = min(int(self.adv.duration / 12), 15)
        self.dragon_gauge_timer = Timer(self.auto_gauge, timeout=max(1, self.conf.gauge_iv), repeat=1).on()
        self.dragon_gauge_pause_timer = None
        self.dragon_gauge_timer_diff = 0
        self.max_gauge = 1000
        self.shift_cost = 500

        # dragondrive
        self.is_dragondrive = False

        # dragonbattle
        self.is_dragonbattle = False

        # logging stuff
        self.act_sum = []
        self.shift_start_time = 0
        self.shift_count = 0

    def auto_gauge(self, t):
        self.charge_gauge(self.dragon_gauge_val, percent=True, auto=True)

    def dhaste(self):
        return self.adv.mod("dh", operator=operator.add)

    def charge_gauge(self, value, utp=False, dhaste=True, percent=False, auto=False):
        dh = self.dhaste() if dhaste else 1
        if utp:
            dh *= self.adv.mod("utph", operator=operator.add)
        if percent:
            value *= self.max_gauge / 100
        value = self.adv.sp_convert(dh, value)
        delta = min(self.dragon_gauge + value, self.max_gauge) - self.dragon_gauge
        # TODO: deal with dragondrive
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

    def d_shift_end(self):
        pass

    def d_shift_partial_end(self):
        pass

    @allow_acl
    def check(self):
        if self.disabled_reasons or self.shift_silence:
            return False
        if self.dragon_gauge < self.shift_cost and not (self.is_dragondrive and self.dragondrive_buff.get()):
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
        self.adv.current_x = DFORM
        self.status = True
        return self.d_shift()
