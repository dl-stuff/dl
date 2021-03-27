from typing import Union
from collections import defaultdict


class Condition(dict):
    def __init__(self, cond, adv):
        self.global_cond = True
        self.base_cond = {}
        self.hp_cond = {">": {}, "<": {}, "=": {}}
        self.adv = adv
        super().__init__({})
        if isinstance(cond, dict):
            self.base_cond = cond
        elif isinstance(cond, bool):
            self.global_cond = cond

    def cond_str(self):
        return " & ".join((k for k, v in self.items() if v))

    def cond_set(self, key, cond=True):
        if key.startswith("hp"):
            try:
                if key[2] == "≤":
                    hp = int(key[3:])
                    op = "<"
                else:
                    hp = int(key[2:])
                    op = ">"
                self.hp_cond[op][hp] = key
                self.hp_cond_update()
                return self[key] and self.global_cond
            except ValueError:
                pass
        elif key.startswith("hit"):
            try:
                hitcount = int(key[3:])
                self[key] = self.adv.hits > hitcount
                self.adv.uses_combo = True
                return self[key] and self.global_cond
            except ValueError:
                pass
        elif key == "zone":
            return self.adv.zonecount > 0 and self.global_cond
        elif key.startswith("amp"):
            amptype = int(key.split("_")[-1])
            return self.adv.amp_lvl(key=amptype) > 0 and self.global_cond
        return self.cond_set_value(key, cond)

    def cond_set_value(self, key, cond=True):
        if key in self.base_cond:
            self[key] = self.base_cond[key]
        elif key not in self:
            self[key] = cond
        return self[key] and self.global_cond

    def hp_cond_update(self):
        current_hp = self.adv.hp
        for hpt, hpt_key in self.hp_cond[">"].items():
            self[hpt_key] = current_hp >= hpt
        for hpt, hpt_key in self.hp_cond["<"].items():
            self[hpt_key] = current_hp <= hpt
        for hpt, hpt_key in self.hp_cond["="].items():
            self[hpt_key] = current_hp == hpt

    def hp_threshold_list(self, threshold=0):
        return sorted(
            filter(
                lambda hp: hp > threshold,
                list(self.hp_cond["="].keys()) + list(self.hp_cond["<"].keys()),
            )
        )

    def exist(self):
        return any(self.values()) and self.global_cond

    def __call__(self, key, cond=True):
        return self.cond_set(key, cond)
