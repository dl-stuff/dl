from core.advbase import *
from conf import DEFAULT
from collections import deque


class Meene(Adv):
    def prerun(self):
        self.butterfly_timers = defaultdict(lambda: set())
        self.act_history = deque(maxlen=6)
        Event("x").listener(self.a1_push_to_act_history, order=0)
        Event("fs").listener(self.a1_push_to_act_history, order=0)
        Event("dodge").listener(self.a1_push_to_act_history, order=0)
        self.cancelable = set()

    def a1_push_to_act_history(self, e):
        self.a1_check_delayed()
        self.act_history.append(e.name)
        log("act_history", str(self.act_history))
        if len(self.act_history) > 5:
            oldest = self.act_history.popleft()
            self.a1_clear_oldest_butterflies(oldest)

    def a1_check_delayed(self):
        for mt, k in self.cancelable.copy():
            if not mt.online and mt.canceled:
                self.a1_clear_butterflies(*k, reason="canceled")
                self.cancelable.remove((mt, k))

    def do_hitattr_make(self, e, aseq, attr, pin=None):
        mt = super().do_hitattr_make(e, aseq, attr, pin=pin)
        if attr.get("butterfly"):
            t = Timer(self.l_a1_clear_butterflies)
            t.name = e.name
            t.chaser = attr.get("butterfly")
            t.start = now()
            t.on(9.001 + attr.get("iv", 0))
            self.butterfly_timers[(now(), e.name, t.chaser)].add(t)
            log("butterflies", "spawn", self.butterflies)
            if mt:
                self.cancelable.add((mt, (now(), e.name, t.chaser)))
        elif mt and attr.get("chaser"):
            self.butterfly_timers[(now(), e.name, attr.get("chaser"))].add(mt)
        while self.butterflies > 9:
            oldest = next(iter(sorted(self.butterfly_timers.keys())))
            for t in self.butterfly_timers[oldest]:
                t.off()
            del self.butterfly_timers[oldest]
            log("butterflies", "cap", self.butterflies)
        if self.butterflies >= 6:
            self.current_s["s1"] = "sixplus"
            self.current_s["s2"] = "sixplus"

    def s1_before(self, e):
        self.a1_check_delayed()
        log("butterflies", self.butterflies)

    def s2_before(self, e):
        self.a1_check_delayed()
        log("butterflies", self.butterflies)

    def s1_proc(self, e):
        self.a1_clear_all_butterflies()

    def s2_proc(self, e):
        self.a1_clear_all_butterflies()

    def a1_clear_all_butterflies(self):
        for chasers in self.butterfly_timers.values():
            for t in chasers:
                t.off()
        self.butterfly_timers = defaultdict(lambda: set())
        self.current_s["s1"] = DEFAULT
        self.current_s["s2"] = DEFAULT
        self.act_history.clear()
        log("butterflies", "remove all", self.butterflies)

    def a1_clear_oldest_butterflies(self, name):
        seq = [k[0] for k in self.butterfly_timers.keys() if k[1] == name]
        if not seq:
            return
        oldest = min(seq)
        matching = tuple(
            filter(
                lambda k: k[1] == name and k[0] == oldest, self.butterfly_timers.keys()
            )
        )
        for m in matching:
            for mt in self.butterfly_timers[m]:
                mt.off()
            del self.butterfly_timers[m]
        if self.butterflies < 6:
            self.current_s["s1"] = DEFAULT
            self.current_s["s2"] = DEFAULT
        log("butterflies", f"remove {name}", self.butterflies)

    def a1_clear_butterflies(self, name, chaser, start, reason="timeout"):
        try:
            key = (name, chaser, start)
            for mt in self.butterfly_timers[key]:
                mt.off()
            del self.butterfly_timers[key]
            if self.butterflies < 6:
                self.current_s["s1"] = DEFAULT
                self.current_s["s2"] = DEFAULT
            log("butterflies", f"{reason} {name}-{chaser}", self.butterflies)
        except KeyError:
            pass

    def l_a1_clear_butterflies(self, t):
        self.a1_clear_butterflies(t.name, t.chaser, t.start)

    @property
    def butterflies(self):
        return len(self.butterfly_timers.keys())

    @property
    def butterflies_s1(self):
        return min(10, self.butterflies)


variants = {None: Meene}
