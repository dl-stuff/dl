from core.advbase import *


class Child_Ranzal(Adv):
    comment = "ignores a1 on non enhanced s1"

    def prerun(self):
        self.crit_mod = self.custom_crit_mod
        self.use_rng = False

    def combine_crit_mods(self):
        m = {"chance": 0, "damage": 0}
        capped_chance = 0
        for order, modifiers in self.all_modifiers["crit"].items():
            for modifier in modifiers:
                if order in m:
                    if order == "chance" and modifier.mod_name not in ("mod_inspired", "hitattr_crit"):
                        capped_chance += modifier.get()
                    else:
                        m[order] += modifier.get()
                else:
                    raise ValueError(f"Invalid crit mod order {order}")
        # 10% cap + 4% axe base
        m["chance"] += min(0.14, capped_chance)

        rate_list = self.build_rates()
        for mask in product(*[[0, 1]] * len(rate_list)):
            p = 1.0
            modifiers = defaultdict(lambda: set())
            for i, on in enumerate(mask):
                cond = rate_list[i]
                cond_name = cond[0]
                cond_p = cond[1]
                if on:
                    p *= cond_p
                    for order, mods in self.all_modifiers[f"{cond_name}_crit"].items():
                        for mod in mods:
                            modifiers[order].add(mod)
                else:
                    p *= 1 - cond_p
            # total += p * reduce(operator.mul, [1 + sum([mod.get() for mod in order]) for order in modifiers.values()], 1.0)
            for order, values in modifiers.items():
                m[order] += p * sum([mod.get() for mod in values])

        chance = min(m["chance"], 1)
        cdmg = m["damage"] + 1.7

        return chance, cdmg

    def custom_crit_mod(self, name=None):
        chance, cdmg = self.combine_crit_mods()
        # check for a1
        if name == "s1" and self.use_rng:
            if random.random() < chance:
                self.add_one_att_amp()
                return cdmg
            else:
                return 1
        average = chance * (cdmg - 1) + 1
        return average


class Child_Ranzal_RNG(Child_Ranzal):
    comment = "allow a1 on non enhanced s1"
    SAVE_VARIANT = False

    def prerun(self):
        super().prerun()
        self.use_rng = True


variants = {None: Child_Ranzal, "RNG": Child_Ranzal_RNG}
