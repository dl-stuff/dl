from core.log import log

class StanceAdv:
    def config_stances(self, stance_dict, default_stance=None, hit_threshold=0, deferred=True):
        """@param: stance_dict[str] -> ModeManager or None"""
        if default_stance is None:
            default_stance = next(iter(stance_dict))
        self.stance = default_stance
        self.hit_threshold = hit_threshold
        self.next_stance = default_stance
        self.stance_dict = stance_dict
        for name, mode in self.stance_dict.items():
            if mode:
                mode.alt['x'].deferred = deferred
            setattr(self, name, lambda: self.queue_stance(name))
        self.update_stance()

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
            log('stance', stance, 'queued')
            self.next_stance = stance
            self.update_stance()
            return True
        if self.can_change_combo():
            self.stance_dict[stance].alt['x'].on()
        return False

    def can_queue_stance(self, stance):
        return (
            stance not in (self.stance, self.next_stance) and 
            not self.Skill._static.silence == 1
        )
    
    def can_change_combo(self):
        return self.hits > self.hit_threshold