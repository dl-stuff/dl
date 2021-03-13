from collections import defaultdict
from functools import reduce
import operator

from core.log import log
from core.timeline import now
from core.advbase import Adv, ReservoirSkill
from core.modifier import ModeManager, EffectBuff
from core.acl import allow_acl, CONTINUE


class StanceAdv(Adv):
    def config_stances(self, stance_dict, default_stance=None, hit_threshold=0, deferred=True):
        """@param: stance_dict[str] -> ModeManager or None"""
        if default_stance is None:
            default_stance = next(iter(stance_dict))
        self.stance = default_stance
        self.hit_threshold = hit_threshold
        self.next_stance = default_stance
        self.stance_dict = stance_dict
        self.has_alt_x = False
        for name, mode in self.stance_dict.items():
            if mode:
                self.has_alt_x = self.has_alt_x or "x" in mode.alt
                try:
                    mode.alt["x"].deferred = deferred
                except KeyError:
                    pass
            queue_stance_fn = self.make_queue_stance_fn(name)
            queue_stance_fn.allow_acl = True
            setattr(self, name, queue_stance_fn)
        self.update_stance()

    def make_queue_stance_fn(self, name):
        return lambda: self.queue_stance(name) and CONTINUE

    def update_stance(self):
        if self.next_stance is not None:
            curr_stance = self.stance_dict[self.stance]
            next_stance = self.stance_dict[self.next_stance]
            if curr_stance is not None:
                curr_stance.off()
                if self.can_change_combo():
                    curr_stance.off()
                else:
                    next_stance.off_except("x")
            if next_stance is not None:
                if self.can_change_combo():
                    next_stance.on()
                else:
                    next_stance.on_except("x")
            self.stance = self.next_stance
            self.next_stance = None

    def x(self, x_min=1):
        if self.can_change_combo():
            self.stance_dict[self.stance].alt["x"].on()
        super().x(x_min=x_min)

    def queue_stance(self, stance):
        if self.can_queue_stance(stance):
            self.next_stance = stance
            self.update_stance()
            return True
        if self.can_change_combo():
            self.stance_dict[stance].alt["x"].on()
        return False

    def can_queue_stance(self, stance):
        return stance not in (self.stance, self.next_stance) and not self.Skill._static.silence == 1

    def can_change_combo(self):
        return (
            self.has_alt_x
            and self.hits >= self.hit_threshold
            and not self.stance_dict[self.stance].alt["x"].get()
            and not self.Skill._static.silence == 1
        )

    @allow_acl
    def s(self, n, stance=None):
        if stance:
            self.queue_stance(stance)
        return super().s(n)


class RngCritAdv(Adv):
    def config_rngcrit(self, cd=0, ev=None, ev_len=None):
        self.rngcrit_cd = False
        self.rngcrit_cd_duration = cd
        if ev:
            self.effect_duration = ev
            self.s_bt = self.mod("buff", operator=operator.add)
            self.x_bt = 1 + self.sub_mod("buff", "ex")
            self.crit_mod = self.ev_custom_crit_mod
            # self.rngcrit_state_len = ev_len or int(((self.effect_duration*self.s_bt) // self.rngcrit_cd_duration) + 1)
            self.rngcrit_states = {(None,): 1.0}
            self.prev_log_time = 0
        else:
            self.crit_mod = self.rand_custom_crit_mod
        if cd > 0:
            self.rngcrit_t = self.Timer(self.rngcrit_cd_off, self.rngcrit_cd_duration)

    def rngcrit_skip(self):
        return False

    def rngcrit_cb(self, mrate=None):
        raise NotImplementedError("Implement rngcrit_cb")

    def rngcrit_cd_off(self, t=None):
        self.rngcrit_cd = False

    def ev_custom_crit_mod(self, name):
        if name == "test" or self.rngcrit_skip():
            return self.solid_crit_mod(name)
        else:
            chance, cdmg = self.combine_crit_mods()
            t = now()

            bt = self.x_bt if not name[0] == "s" or name == "ds" else self.s_bt

            new_states = defaultdict(lambda: 0.0)
            for state, state_p in self.rngcrit_states.items():
                state = tuple([b for b in state if b is not None and sum(b) > t])
                if not state:
                    state = (None,)
                if state[0] is not None and t - state[0][0] < self.rngcrit_cd_duration:
                    new_states[state] += state_p
                else:
                    miss_rate = 1.0 - chance
                    new_states[state] += miss_rate * state_p
                    newest = (t, self.effect_duration * bt)
                    new_states[(newest,) + state] = chance * state_p
            new_states[(None,)] += 1 - sum(new_states.values())
            mrate = reduce(
                lambda mv, s: mv + (sum(int(b is not None) for b in s[0]) * s[1]),
                new_states.items(),
                0,
            )
            if self.prev_log_time == 0 or self.prev_log_time < t - self.rngcrit_cd_duration:
                self.prev_log_time = t
            self.rngcrit_cb(mrate)
            self.rngcrit_states = new_states

            return chance * (cdmg - 1) + 1

    def rand_custom_crit_mod(self, name):
        if self.rngcrit_cd or name == "test" or self.rngcrit_skip():
            return self.solid_crit_mod(name)
        else:
            crit = self.rand_crit_mod(name)
            if crit > 1:
                self.rngcrit_cb()
                if self.rngcrit_cd_duration > 0:
                    self.rngcrit_cd = True
                    self.rngcrit_t.on()
            return crit


class SigilAdv(Adv):
    def config_sigil(self, duration=300, **kwargs):
        self.unlocked = False
        self.locked_sigil = EffectBuff("locked_sigil", 300, lambda: None, self.a_sigil_unlock).no_bufftime()
        self.locked_sigil.on()
        self.sigil_mode = ModeManager(group="sigil", **kwargs)

    def a_sigil_unlock(self):
        self.unlocked = now()
        self.sigil_mode.on()

    def a_update_sigil(self, time):
        if not self.unlocked:
            duration = self.locked_sigil.buff_end_timer.add(time)
            if duration <= 0:
                self.locked_sigil.off()
                self.a_sigil_unlock()

    def post_run(self, end):
        if self.comment:
            self.comment += "; "
        if self.unlocked:
            self.comment += f"unlock at {self.unlocked:.02f}s"
        else:
            self.comment += f"not unlocked"


class ArmamentAdv(Adv):
    def __init__(self, true_sp=999999, maxcharge=2, **kwargs):
        super().__init__(**kwargs)
        self.sr = ReservoirSkill(name="s1", true_sp=true_sp, maxcharge=maxcharge)
        self.a_s_dict["s1"] = self.sr
        self.a_s_dict["s2"] = self.sr

    def config_armament(self, autocharge=80000):
        self.current_s["s1"] = "base1"
        self.current_s["s2"] = "base2"
        self.sr.autocharge_init(autocharge).on()

    @property
    def skills(self):
        return (self.sr, self.s3, self.s4)

    @allow_acl
    def s(self, n):
        sn = f"s{n}"
        if n == 1 or n == 2:
            if self.sr.count == self.sr.maxcharge and f"max{n}" in self.sr.act_dict:
                self.current_s[sn] = f"max{n}"
            else:
                self.current_s[sn] = f"base{n}"
            return self.sr(call=n)
        else:
            return self.a_s_dict[sn]()

    def charge_p(self, name, percent, target=None, no_autocharge=False):
        percent = percent / 100 if percent > 1 else percent
        targets = self.get_targets(target)
        if not targets:
            return
        for s in targets:
            if s != self.sr and no_autocharge and hasattr(s, "autocharge_timer"):
                continue
            s.charge(self.sp_convert(percent, s.sp))
        log(
            "sp",
            name if not target else f"{name}->{target}",
            f"{percent*100:.0f}%",
            f"{self.sr.charged}/{self.sr.sp} ({self.sr.count}), {self.s3.charged}/{self.s3.sp}, {self.s4.charged}/{self.s4.sp}",
        )
        self.think_pin("prep")

    def charge(self, name, sp, target=None):
        sp = self.sp_convert(self.sp_mod(name), sp)
        targets = self.get_targets(target)
        if not targets:
            return
        for s in targets:
            if name[0] == "x" and s == self.sr:
                continue
            s.charge(sp)
        log(
            "sp",
            name,
            sp,
            f"{self.sr.charged}/{self.sr.sp} ({self.sr.count}), {self.s3.charged}/{self.s3.sp}, {self.s4.charged}/{self.s4.sp}",
        )
        self.think_pin("sp")
