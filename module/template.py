from core.log import log
from core.advbase import Adv

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
                self.has_alt_x = self.has_alt_x or 'x' in mode.alt
                try:
                    mode.alt['x'].deferred = deferred
                except KeyError:
                    pass
            setattr(self, name, lambda: self.queue_stance(name))

    def update_stance(self):
        if self.next_stance is not None:
            curr_stance = self.stance_dict[self.stance]
            next_stance = self.stance_dict[self.next_stance]
            if curr_stance is not None:
                curr_stance.off()
            if next_stance is not None:
                next_stance.on_except('x')
            self.stance = self.next_stance
            self.next_stance = None

    def queue_stance(self, stance):
        if self.can_queue_stance(stance):
            self.next_stance = stance
            self.update_stance()
            return True
        if self.can_change_combo():
            try:
                self.stance_dict[stance].alt['x'].on()
            except KeyError:
                pass
        return False

    def can_queue_stance(self, stance):
        return (
            stance not in (self.stance, self.next_stance) and 
            not self.Skill._static.silence == 1
        )
    
    def can_change_combo(self):
        return self.has_alt_x and self.hits >= self.hit_threshold

    def s(self, n, stance=None):
        if stance:
            self.queue_stance(stance)
        return super().s(n)


class RngCritAdv(Adv):

    def config_rngcrit(self, cd=0):
        self.crit_mod = self.custom_crit_mod
        self.rngcrit_cd = False
        self.rngcrit_cd_duration = cd
        if cd > 0:
            self.rngcrit_t = self.Timer(self.rngcrit_cd_off, self.rngcrit_cd_duration)

    def rngcrit_skip(self):
        return False

    def rngcrit_cb(self):
        raise NotImplementedError('Implement rngcrit_cb')

    def rngcrit_cd_off(self, t=None):
        self.rngcrit_cd = False

    def custom_crit_mod(self, name):
        if self.rngcrit_cd or name == 'test' or self.rngcrit_skip():
            return self.solid_crit_mod(name)
        else:
            crit = self.rand_crit_mod(name)
            if crit > 1 and not self.rngcrit_cd:
                self.rngcrit_cb()
                if self.rngcrit_cd_duration > 0:
                    self.rngcrit_cd = True
                    self.rngcrit_t.on()
            return crit

