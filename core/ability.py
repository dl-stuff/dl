import random

from core.log import log
from core.afflic import AFFLICT_LIST
from conf import ELEMENTS, WEAPON_TYPES


class Ability:
    def __init__(self, name, mod=None):
        self.name = name
        self.mod = mod or []
        self.BYPASS_NIHIL = False

    def check_ele_wt(self, m, adv):
        cond = m[3]
        if "_" in cond:
            classifier, cond = cond.split("_", 1)
        else:
            classifier = cond
            cond = None
        new_m = (m[0], m[1], m[2], cond)
        if classifier in ELEMENTS:
            return adv.slots.c.ele == classifier, new_m
        elif classifier in WEAPON_TYPES:
            return adv.slots.c.wt == classifier, new_m
        else:
            return True, m

    def oninit(self, adv, afrom=None):
        for idx, m in enumerate(self.mod):
            if len(m) > 3 and m[3] is not None:
                is_ele_wt, m = self.check_ele_wt(m, adv)
                if not is_ele_wt:
                    continue
            mod_name = "{}_{}".format(afrom, idx)
            if m[1] == "buff" and adv.nihilism and not self.BYPASS_NIHIL:
                continue
            self.mod_object = adv.Modifier(mod_name, *m)
            if m[1] == "buff":
                adv.Buff(
                    f"{mod_name}_buff",
                    duration=-1,
                    modifier=self.mod_object,
                    source="ability",
                ).on()


ability_dict = {}


class Strength(Ability):
    def __init__(self, name, value, cond=None):
        if cond == "ex":
            super().__init__(name, [("att", "ex", value)])
        else:
            super().__init__(name, [("att", "passive", value, cond)])


ability_dict["a"] = Strength
ability_dict["au"] = Strength  # united strength


class Resist(Ability):
    def __init__(self, name, value, cond=None):
        if not cond or cond.startswith("hp"):
            super().__init__(name, [(name, "passive", value, cond)])
        else:
            super().__init__(name, [(name, "buff", value, cond)])
            self.BYPASS_NIHIL = True


ability_dict["res"] = Resist


class Affliction_Resist(Ability):
    def __init__(self, name, value, cond=None):
        atype = name.split("_")[1]
        if self.atype == "all":
            super().__init__(name, [("affres", aff, value, cond) for aff in AFFLICT_LIST])
        else:
            super().__init__(name, [("affres", atype, value, cond)])


ability_dict["affres"] = Affliction_Resist


class Skill_Damage(Ability):
    def __init__(self, name, value, cond=None):
        if cond == "ex":
            super().__init__(name, [("s", "ex", value)])
        else:
            super().__init__(name, [("s", "passive", value, cond)])


ability_dict["s"] = Skill_Damage
ability_dict["sd"] = Skill_Damage


class Force_Strike(Ability):
    def __init__(self, name, value, cond=None):
        if cond == "ex":
            super().__init__(name, [("fs", "ex", value)])
        else:
            super().__init__(name, [("fs", "passive", value, cond)])


ability_dict["fs"] = Force_Strike


class Standard_Attack(Ability):
    def __init__(self, name, value, cond=None):
        if cond == "ex":
            super().__init__(name, [("x", "ex", value)])
        else:
            super().__init__(name, [("x", "passive", value, cond)])


ability_dict["x"] = Standard_Attack


class Health_Points(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [("maxhp", "passive", value, cond)])


ability_dict["hp"] = Health_Points


class Recovery_Potency(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [("recovery", "passive", value, cond)])


ability_dict["rcv"] = Recovery_Potency


class Buff_Time(Ability):
    def __init__(self, name, value, cond=None):
        if cond == "ex":
            super().__init__(name, [("buff", "ex", value)])
        else:
            super().__init__(name, [("buff", "passive", value, cond)])


ability_dict["bt"] = Buff_Time


class Debuff_Time(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [("debuff", "passive", value, cond)])


ability_dict["dbt"] = Debuff_Time


class Elemental_Damage(Ability):
    def __init__(self, name, value, cond=None):
        _, element = name.split("_")
        super().__init__(name, [(element, "ele", value, cond)])


ability_dict["ele"] = Elemental_Damage


class ConditionalModifierAbility(Ability):
    def __init__(self, name, mtype, morder, value, cond=None):
        if "_" in name:
            afflict = name.split("_", 1)[1]
            super().__init__(name, [(f"{afflict}_{mtype}", morder, value, cond)])
        else:
            super().__init__(name, [(mtype, morder, value, cond)])


class Critical_Chance(ConditionalModifierAbility):
    def __init__(self, name, value, cond=None):
        super().__init__(name, "crit", "chance", value, cond)


ability_dict["cc"] = Critical_Chance
ability_dict["ccu"] = Critical_Chance  # united crit


class Critical_Damage(ConditionalModifierAbility):
    def __init__(self, name, value, cond=None):
        super().__init__(name, "crit", "damage", value, cond)


ability_dict["cd"] = Critical_Damage


class Killer(ConditionalModifierAbility):
    def __init__(self, name, value, cond=None):
        super().__init__(name, "killer", "passive", value, cond)


ability_dict["k"] = Killer


class Skill_Haste(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [("sp", "passive", value, cond)])


ability_dict["sp"] = Skill_Haste
ability_dict["spu"] = Skill_Haste  # united haste


class Striking_Haste(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [("spf", "passive", value, cond)])


ability_dict["spf"] = Striking_Haste


class Broken_Punisher(Ability):
    EFFICIENCY = 0.15

    def __init__(self, name, value, cond=None):
        super().__init__(name, [("att", "bk", value * self.EFFICIENCY, cond)])

    def oninit(self, adv, afrom=None):
        if not adv.conf["berserk"]:
            super().oninit(adv, afrom=afrom)


ability_dict["bk"] = Broken_Punisher


class Overdrive_Punisher(Ability):
    EFFICIENCY = 0.45

    def __init__(self, name, value, cond=None):
        self.value = value
        self.cond = cond
        super().__init__(name, [("killer", "passive", value, cond)])

    def oninit(self, adv, afrom=None):
        if not adv.conf["berserk"]:
            self.mod = [("killer", "passive", self.value * self.EFFICIENCY, self.cond)]
        super().oninit(adv, afrom=afrom)


ability_dict["od"] = Overdrive_Punisher


class Gauge_Accelerator(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [("odaccel", "passive", value, cond)])


ability_dict["odaccel"] = Gauge_Accelerator


class Dragon_Damage(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [("da", "passive", value, cond)])


ability_dict["da"] = Dragon_Damage


class Dragon_Time(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [("dt", "passive", value, cond)])


ability_dict["dt"] = Dragon_Time


class Dragon_Haste(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [("dh", "passive", value, cond)])


ability_dict["dh"] = Dragon_Haste


class Attack_Speed(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [("spd", "passive", value, cond)])


ability_dict["spd"] = Attack_Speed


class Charge_Speed(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [("cspd", "passive", value, cond)])


ability_dict["cspd"] = Charge_Speed


class Force_Strike_Speed(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [("fspd", "buff", value, cond)])


ability_dict["fspd"] = Force_Strike_Speed


class Combo_Time(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [("ctime", "passive", value, cond)])


ability_dict["ctime"] = Combo_Time


class Bleed_Killer(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [("bleed_killer", "passive", value, cond)])


ability_dict["bleed"] = Bleed_Killer


class Union_Ability(Ability):
    UNION_MAP = {
        1: {4: [("s", "passive", 0.10)]},
        2: {4: [("att", "bk", 0.10 * Broken_Punisher.EFFICIENCY)]},
        3: {4: [("att", "passive", 0.08)]},
        4: {3: [("sp", "passive", 0.06)], 4: [("sp", "passive", 0.10)]},
        5: {
            2: [("da", "passive", 0.10)],
            3: [("da", "passive", 0.18)],
            4: [("da", "passive", 0.30)],
        },
        6: {
            2: [("fs", "passive", 0.05)],
            3: [("fs", "passive", 0.08)],
            4: [("fs", "passive", 0.15)],
        },
        7: {2: [("affres", "burn", 100)]},
        8: {2: [("affres", "stun", 100)]},
        9: {2: [("affres", "para", 100)]},
        10: {2: [("affres", "curse", 100)]},
        11: {
            2: [("buff", "passive", 0.05)],
            3: [("buff", "passive", 0.08)],
            4: [("buff", "passive", 0.15)],
        },
        12: {2: [("affres", "poison", 100)]},
        13: {2: [("affres", "freeze", 100)]},
        14: {2: [("affres", "blind", 100)]},
        15: {2: [("affres", "bog", 100)]},
        16: {2: [("affres", "sleep", 100)]},
    }

    def __init__(self, name, value, level):
        self.union_id = value
        self.union_lv = level
        mod = self.UNION_MAP[value][min(level, max(self.UNION_MAP[value]))]
        super().__init__(name, mod.copy())

    def oninit(self, adv, afrom=None):
        if not (adv.conf["berserk"] and self.union_id == 2):
            super().oninit(adv, afrom=afrom)


ability_dict["union"] = Union_Ability


class BuffingAbility(Ability):
    def __init__(self, name, value, duration=-1, cooldown=None):
        self.buff_args = (name, value, duration, "att", "buff")
        if "_" in name:
            # how dum
            extra_args = (arg.replace("-", "_") for arg in name.split("_")[1:])
            self.buff_args = (name, value, duration, *extra_args)
        self.cooldown = cooldown
        if self.cooldown:
            self.cooldown -= 0.0001
        super().__init__(name)


class ConditionalBuffingAbility(BuffingAbility):
    def __init__(self, name, value, duration=-1, cooldown=None):
        super().__init__(name, value, duration=duration, cooldown=cooldown)
        self.threshold = float(self.buff_args[3])
        self.buff_args = (name, value, -1, *self.buff_args[4:])


class HpCheck_Buff(ConditionalBuffingAbility):
    def check_hp(self, hp):
        raise NotImplementedError("check_hp")

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return False

        self.buff_object = adv.Buff(*self.buff_args)
        if self.check_hp(adv.hp):
            self.buff_object.on()

        if self.cooldown:

            def l_hpcheck(t):
                if self.check_hp(adv.hp):
                    self.buff_object.on()
                else:
                    self.hp_check_timer.off()

            self.hp_check_timer = adv.Timer(l_hpcheck, self.cooldown, True)

            def l_hpchanged(e):
                if not self.hp_check_timer.online and self.check_hp(adv.hp):
                    self.buff_object.on()
                    self.hp_check_timer.on()
                else:
                    self.hp_check_timer.off()

        else:

            def l_hpchanged(e):
                if self.check_hp(adv.hp):
                    self.buff_object.on()
                else:
                    self.buff_object.off()

        adv.Event("hp").listener(l_hpchanged)
        return True


class HpMore_Buff(HpCheck_Buff):
    def check_hp(self, hp):
        return hp >= self.threshold

    def oninit(self, adv, afrom=None):
        if super().oninit(adv, afrom=afrom):
            adv.condition(f"hp{int(self.threshold)}")


ability_dict["hpmore"] = HpMore_Buff


class HpLess_Buff(HpCheck_Buff):
    def check_hp(self, hp):
        return hp <= self.threshold

    def oninit(self, adv, afrom=None):
        if super().oninit(adv, afrom=afrom):
            adv.condition(f"hp≤{int(self.threshold)}")


ability_dict["hpless"] = HpLess_Buff


class Hitcount_Buff(ConditionalBuffingAbility):
    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return
        self.threshold = int(self.threshold)
        adv.condition(f"hit{self.threshold}")
        self.buff_object = adv.Buff(*self.buff_args)
        self.add_combo_o = adv.add_combo

        def add_combo(name="#"):
            result = self.add_combo_o(name)
            if adv.hits > self.threshold:
                self.buff_object.on()
            else:
                self.buff_object.off()
            return result

        adv.add_combo = add_combo


ability_dict["hitcount"] = Hitcount_Buff


class Last_Buff(BuffingAbility):
    HEAL_TO = 30

    def __init__(self, name, value, duration=15, chances=1):
        super().__init__(name, value, duration)
        self.proc_chances = chances
        self.auto_proc = "regen" not in self.buff_args
        Last_Buff.HEAL_TO = 30

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        def l_lo_buff(e):
            if self.proc_chances > 0 and e.hp <= 30 and (e.hp - e.delta) > 30:
                self.proc_chances -= 1
                adv.Buff(*self.buff_args).no_bufftime().on()

        adv.Event("hp").listener(l_lo_buff)
        if self.auto_proc and "hp" not in adv.conf and adv.condition("last offense"):

            def lo_damaged(t):
                if adv.hp > 30 and self.proc_chances > 0:
                    next_hp = adv.condition.hp_threshold_list()
                    if next_hp and next_hp[0] < 30:
                        adv.set_hp(next_hp)
                    else:
                        adv.set_hp(30)
                    adv.Timer(lo_healed).on(10)

            def lo_healed(t):
                next_hp = adv.condition.hp_threshold_list(Last_Buff.HEAL_TO)
                try:
                    adv.set_hp(next_hp[0])
                except:
                    adv.set_hp(100)

            adv.Timer(lo_damaged).on(0.1)


ability_dict["lo"] = Last_Buff


class Doublebuff(BuffingAbility):
    def __init__(self, name, value, duration=15, cooldown=None):
        super().__init__(name, value, duration, cooldown)

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        if self.name == "bc_energy":

            def defchain(e):
                if adv.is_set_cd(afrom, self.cooldown):
                    return
                if hasattr(e, "rate"):
                    adv.energy.add(self.buff_args[1] * e.rate)
                else:
                    adv.energy.add(self.buff_args[1])

            adv.Event("defchain").listener(defchain)
        else:

            def defchain(e):
                if adv.is_set_cd(afrom, self.cooldown):
                    return
                adv.set_cd(afrom, self.cooldown)
                if hasattr(e, "rate"):
                    adv.Buff(
                        self.buff_args[0],
                        self.buff_args[1] * e.rate,
                        *self.buff_args[2:],
                        source=e.source,
                    ).on()
                else:
                    adv.Buff(*self.buff_args, source=e.source).on()

            adv.Event("defchain").listener(defchain)


ability_dict["bc"] = Doublebuff


class Slayer_Strength(BuffingAbility):
    def __init__(self, name, value):
        super().__init__(name, value, -1)

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        self.stacks = 0
        self.slayed = 0

        def l_slayed(e):
            if self.stacks >= 5:
                return
            need_count = 5
            if self.name.startswith("sts"):
                if not e.name.startswith("fs"):
                    return
                need_count = 3
            self.slayed += e.count
            while self.slayed >= need_count and self.stacks < 5:
                adv.Buff(*self.buff_args).on()
                self.stacks += 1
                self.slayed -= need_count

        adv.Event("slayed").listener(l_slayed)


ability_dict["sls"] = Slayer_Strength
ability_dict["sts"] = Slayer_Strength


class Dragon_Buff(Ability):
    def __init__(self, name, *args):
        self.buff_args = name.split("_")[1:]
        self.dc_values = args
        try:
            self.mod_order = self.buff_args[1]
        except IndexError:
            self.mod_order = None
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        if adv.nihilism and self.mod_order != "passive":
            return

        self.dc_level = 0

        def l_dc_buff(t):
            if self.dc_level < len(self.dc_values):
                buff = adv.Buff(self.name, self.dc_values[self.dc_level], -1, *self.buff_args)
                if buff.mod_order == "passive":
                    buff.hidden = True
                buff.on()
                self.dc_level += 1

        adv.Event("dragon").listener(l_dc_buff)


ability_dict["dshift"] = Dragon_Buff


class Dragon_AltSkill(Ability):
    def __init__(self, name, shift_req, *args):
        self.shift_req = shift_req
        self.buff_args = args
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        from core.modifier import SAltBuff

        def l_dc_buff(t):
            if adv.dragonform.shift_count == self.shift_req:
                SAltBuff(self.name, *self.buff_args).on()

        adv.Event("dragon").listener(l_dc_buff)


ability_dict["dsalt"] = Dragon_AltSkill


class Resilient_Offense(BuffingAbility):
    def __init__(self, name, value, interval=None):
        self.interval = interval
        duration = -1
        if name.startswith("ro"):
            self.proc_chances = 3
            self.hp_threshold = 30
        elif name.startswith("uo"):
            self.proc_chances = 5
            self.hp_threshold = 70
        elif name.startswith("nyar"):
            self.proc_chances = float("inf")
            self.hp_threshold = 30
            duration = 20
        super().__init__(name, value, duration)

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        def l_ro_buff(e):
            if self.proc_chances is self.proc_chances > 0 and e.hp <= 30 and (e.hp - e.delta) > 30:
                self.proc_chances -= 1
                adv.Buff(*self.buff_args).on()

        adv.Event("hp").listener(l_ro_buff)
        if self.interval and "hp" not in adv.conf:

            def ro_damaged(t):
                if adv.hp > self.hp_threshold:
                    next_hp = adv.condition.hp_threshold_list()
                    if next_hp and next_hp[0] < self.hp_threshold:
                        adv.set_hp(next_hp)
                    else:
                        adv.set_hp(self.hp_threshold)
                    adv.Timer(ro_healed).on(10)

            def ro_healed(t):
                next_hp = adv.condition.hp_threshold_list(self.hp_threshold)
                try:
                    adv.set_hp(next_hp[0])
                except:
                    adv.set_hp(100)

            if self.interval < adv.duration and adv.condition(f"hp={self.hp_threshold}% every {self.interval}s"):
                for i in range(1, self.proc_chances):
                    adv.Timer(ro_damaged).on(self.interval * i)
            adv.Timer(ro_damaged).on(0.1)


ability_dict["ro"] = Resilient_Offense
ability_dict["uo"] = Resilient_Offense
ability_dict["nyar"] = Resilient_Offense


class Skill_Prep(Ability):
    def __init__(self, name, value, cond=None):
        self.value = value
        if isinstance(self.value, str):
            self.value = float(value.replace("%", ""))
        if self.value > 1:
            self.value /= 100
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        adv.charge_p("skill_prep", self.value)


ability_dict["prep"] = Skill_Prep


class Buff_Prep(BuffingAbility):
    def __init__(self, name, value, duration=180):
        super().__init__(name, value, duration)

    def oninit(self, adv, afrom=None):
        adv.Buff(*self.buff_args).ex_bufftime().on()


ability_dict["bprep"] = Buff_Prep


class Primed(BuffingAbility):
    def __init__(self, name, value, duration=10, cooldown=15):
        super().__init__(name, value, duration, cooldown)

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        primed_buff = adv.Buff(*self.buff_args).ex_bufftime()

        def l_primed(e):
            if not adv.is_set_cd(afrom, self.cooldown):
                primed_buff.on()

        adv.Event("s1_charged").listener(l_primed)


ability_dict["primed"] = Primed


class Dragon_Prep(Ability):
    def __init__(self, name, value):
        self.value = value
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        adv.dragonform.charge_gauge(self.value, percent=True, dhaste=False)


ability_dict["dp"] = Dragon_Prep


class Affliction_Guard(Ability):
    def __init__(self, name, value):
        self.value = value
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        adv.afflict_guard = self.value


ability_dict["ag"] = Affliction_Guard


class Energy_Prep(Ability):
    def __init__(self, name, value):
        self.energy_count = value
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        adv.energy.add(self.energy_count)


ability_dict["eprep"] = Energy_Prep


class Force_Charge(Ability):
    def __init__(self, name, charge, value=0.25):
        self.charge = charge
        self.value = value
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        if hasattr(adv, "fs_prep_c"):
            adv.fs_prep_v += self.value
        else:

            def l_fs_charge(e):
                if not e.is_hit:
                    return
                adv.charge_p(self.name, adv.fs_prep_v)
                self.charge -= 1
                adv.fs_prep_c = self.charge
                if self.charge == 0:
                    self.l_fs_charge.off()

            self.l_fs_charge = adv.Listener("fs-h", l_fs_charge)

            i = 1
            fsi = f"fs{i}"
            while hasattr(adv, fsi):
                self.l_fs_charge = adv.Listener(fsi, l_fs_charge)
                i += 1
                fsi = f"fs{i}"
            adv.fs_prep_c = self.charge
            adv.fs_prep_v = self.value


ability_dict["fsprep"] = Force_Charge


class Energized_Buff(BuffingAbility):
    def __init__(self, name, value, duration=15, cooldown=None):
        super().__init__(name, value, duration)

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        def l_energized(e):
            if e.stack >= 5:
                adv.Buff(*self.buff_args).on()

        adv.Event("energy").listener(l_energized)


ability_dict["energized"] = Energized_Buff


class Energy_Buff(BuffingAbility):
    def __init__(self, name, value, duration=15, cooldown=15):
        super().__init__(name, value, duration, cooldown)

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        if self.name == "energy_inspiration":

            def l_energy(e):
                if not adv.is_set_cd(afrom, self.cooldown):
                    adv.inspiration.add(self.buff_args[1])

        else:

            def l_energy(e):
                if not adv.is_set_cd(afrom, self.cooldown):
                    adv.Buff(*self.buff_args).on()

        adv.Event("energy").listener(l_energy)


ability_dict["energy"] = Energy_Buff


class Affliction_Selfbuff(Ability):
    def __init__(self, name, value, duration=15, cooldown=10, is_rng=False):
        nameparts = name.split("_")
        self.atype = nameparts[1].strip()
        self.value = value
        self.duration = duration
        self.buff_args = nameparts[2:]
        self.cooldown = cooldown
        self.is_rng = is_rng
        super().__init__(name)

    def oninit(self, adv, afrom=None, bufftype=None):
        if adv.nihilism:
            return

        bufftype = bufftype or adv.Buff

        def l_afflict(e):
            if self.is_rng:
                if random.random() < e.rate and not adv.is_set_cd(afrom, self.cooldown):
                    bufftype(
                        self.name,
                        self.value,
                        self.duration,
                        *self.buff_args,
                        source=e.source,
                    ).on()
            elif e.rate > 0 and adv.is_set_cd(afrom, self.cooldown):
                bufftype(
                    self.name,
                    self.value * e.rate,
                    self.duration,
                    *self.buff_args,
                    source=e.source,
                ).on()

        adv.Event(self.atype).listener(l_afflict)


ability_dict["affself"] = Affliction_Selfbuff


class Affliction_Teambuff(Affliction_Selfbuff):
    def oninit(self, adv, afrom=None):
        super().oninit(adv, afrom=afrom, bufftype=adv.Teambuff)


ability_dict["affteam"] = Affliction_Teambuff


class AntiAffliction_Selfbuff(Affliction_Selfbuff):
    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        def l_afflict(e):
            if e.rate < 1 and adv.is_set_cd(afrom, self.cooldown):
                adv.Buff(
                    self.name,
                    self.value * (1 - e.rate),
                    self.duration,
                    *self.buff_args,
                    source=e.source,
                ).on()

        adv.Event(self.atype).listener(l_afflict)


ability_dict["antiaffself"] = AntiAffliction_Selfbuff


class Potent_Affres(Affliction_Selfbuff):
    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        def l_afflict(e):
            if e.atype == self.atype and adv.is_set_cd(afrom, self.cooldown):
                adv.Buff(self.name, self.value, self.duration, *self.buff_args, source=None).on()

        adv.Event("selfaff").listener(l_afflict)


ability_dict["resself"] = Potent_Affres


class Energy_Stat(Ability):
    STAT_LEVELS = {
        ("att", "passive"): {
            3: (0.0, 0.04, 0.06, 0.08, 0.10, 0.20),
            7: (0.0, 0.05, 0.10, 0.20, 0.30, 0.40),
            "chariot": (0.0, 0.25, 0.30, 0.35, 0.40, 0.45),
        },
        ("crit", "chance"): {
            3: (0.0, 0.01, 0.02, 0.03, 0.04, 0.08),
            7: (0.0, 0.01, 0.04, 0.07, 0.10, 0.15),
        },
        ("sp", "passive"): {
            3: (0.0, 0.05, 0.10, 0.15, 0.20, 0.25),
        },
    }

    def __init__(self, name, value):
        parts = name.split("_")
        self.mtype = parts[1]
        try:
            self.morder = parts[2]
        except IndexError:
            self.morder = "chance" if self.mtype == "crit" else "passive"
        self.stat_values = Energy_Stat.STAT_LEVELS[(self.mtype, self.morder)][value]
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        from core.advbase import log

        stat_mod = adv.Modifier(self.name, self.mtype, self.morder, 0.0)

        def l_energy(e):
            stat_mod.mod_value = self.stat_values[round(adv.energy.stack)]
            log(self.name, stat_mod.mod_value, adv.energy.stack)

        adv.Event("energy").listener(l_energy)
        adv.Event("energy_end").listener(l_energy)


ability_dict["estat"] = Energy_Stat


class Energy_Haste(Ability):
    HASTE_LEVELS = {
        3: (0.0, 0.05, 0.10, 0.15, 0.20, 0.25),
    }

    def __init__(self, name, value):
        # self.atk_buff = Selfbuff('a1atk',0.00,-1,'att','passive').on()
        # self.a1crit = Selfbuff('a1crit',0.00,-1,'crit','chance').on()
        self.haste_values = self.STR_LEVELS[value]
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        self.haste_buff = adv.Selfbuff("ehaste", 0.00, -1, "sp", "passive").on()

        def l_energy(e):
            self.haste_buff.off()
            self.haste_buff.set(self.haste_values[round(e.stack)])
            self.haste_buff.on()

        adv.Event("energy").listener(l_energy)


ability_dict["ehaste"] = Energy_Stat


class Affliction_Edge(Ability):
    def __init__(self, name, value, cond=None):
        self.atype = name.split("_")[1]
        super().__init__(name, [("edge", self.atype, value, cond)])

    def oninit(self, adv, afrom=None):
        super().oninit(adv, afrom)
        if self.atype == "all":
            for aff in AFFLICT_LIST:
                adv.afflics.__dict__[aff].aff_edge_mods.append(self.mod_object)
        else:
            adv.afflics.__dict__[self.atype].aff_edge_mods.append(self.mod_object)


ability_dict["edge"] = Affliction_Edge


class Affliction_Time(Ability):
    def __init__(self, name, value, cond=None):
        self.atype = name.split("_")[1]
        super().__init__(name, [("afftime", self.atype, value, cond)])

    def oninit(self, adv, afrom=None):
        super().oninit(adv, afrom)
        if self.atype == "all":
            for aff in AFFLICT_LIST:
                adv.afflics.__dict__[aff].aff_time_mods.append(self.mod_object)
        else:
            adv.afflics.__dict__[self.atype].aff_time_mods.append(self.mod_object)


ability_dict["afftime"] = Affliction_Time


class ComboProcAbility(Ability):
    def __init__(self, name, value, cond=None):
        self.threshold = value
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        if adv.condition("always connect hits"):
            self.add_combo_o = adv.add_combo
            self.ehit = 0

            def add_combo(name="#"):
                result = self.add_combo_o(name)
                if not result:
                    self.combo_reset_cb()
                    self.ehit == 0
                else:
                    n_ehit = adv.hits // self.threshold
                    if n_ehit > self.ehit:
                        self.combo_proc_cb(adv, n_ehit - self.ehit)
                        self.ehit = n_ehit
                return result

            adv.add_combo = add_combo

    def combo_proc_cb(self, adv, delta):
        raise NotImplementedError("combo_proc_cb")

    def combo_reset_cb(self):
        pass


class Energy_Combo(ComboProcAbility):
    def combo_proc_cb(self, adv, delta):
        if adv.nihilism:
            return

        adv.energy.add(delta)


ability_dict["ecombo"] = Energy_Combo


class DPrep_Combo(ComboProcAbility):
    def combo_proc_cb(self, adv, delta):
        adv.dragonform.charge_gauge(delta * 3, dhaste=False, percent=True)


ability_dict["dpcombo"] = DPrep_Combo


class Crit_Combo_Resetable(ComboProcAbility):
    def __init__(self, name, value, threshold, limit):
        self.value = value
        self.limit = limit * value
        super().__init__(name, threshold)

    def oninit(self, adv, afrom=None):
        super().oninit(adv, afrom=afrom)
        self.combo_crit_mod = adv.Modifier(self.name, "crit", "chance", 0.0)

    def combo_proc_cb(self, adv, delta):
        self.combo_crit_mod.mod_value = min(self.limit, (adv.hits // self.threshold) * self.value)

    def combo_reset_cb(self):
        self.combo_crit_mod.mod_value = 0


ability_dict["critcombo"] = Crit_Combo_Resetable


class Skill_Recharge(Ability):
    def __init__(self, name, value):
        self.all = name == "scharge_all"
        self.value = value
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        if self.all:

            def l_skill_charge(e):
                # dform eats this sp
                if not e.name.startswith("ds"):
                    adv.charge_p("scharge", self.value)

        else:

            def l_skill_charge(e):
                try:
                    if not e.name.startswith("ds"):
                        adv.charge_p("scharge", self.value, target=e.base, no_autocharge=True)
                except AttributeError:
                    pass

        adv.Event("s").listener(l_skill_charge, order=0)


ability_dict["scharge"] = Skill_Recharge


class Energy_Extra(Ability):
    def __init__(self, name, value, rng=False):
        self.use_rng = rng
        self.value = value
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        if self.use_rng:

            def l_energy(e):
                if random.random() < self.value:
                    adv.energy.add_extra(1)

        else:

            def l_energy(e):
                adv.energy.add_extra(self.value)  # means

        adv.Event("energy").listener(l_energy)


ability_dict["eextra"] = Energy_Extra


class Damaged_Buff(BuffingAbility):
    def __init__(self, name, value, duration=15, cooldown=5):
        super().__init__(name, value, duration, cooldown)

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        from core.modifier import SingleActionBuff

        if self.buff_args[1] == "fs":
            self.damaged_buff = SingleActionBuff(*self.buff_args)

            def l_damaged_buff(e):
                if e.delta < 0 and e.source != "dot":
                    self.damaged_buff.on()

        else:

            def l_damaged_buff(e):
                if e.delta < 0 and e.source != "dot" and adv.is_set_cd(afrom, self.cooldown):
                    adv.Buff(*self.buff_args).on()

        adv.Event("hp").listener(l_damaged_buff)


ability_dict["damaged"] = Damaged_Buff


class Poised_Buff(Ability):
    def __init__(self, name, value, passive=False):
        self.value = value
        self.buff_args = (arg.replace("-", "_") for arg in name.split("_")[1:])
        self.passive = passive
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        from core.modifier import ZoneTeambuff

        self.poised_buff = adv.Buff(self.name, self.value, -1, *self.buff_args)
        if self.passive:
            self.poised_buff.hidden = True

        def l_poised_buff(e):
            if isinstance(e.buff, ZoneTeambuff):
                self.poised_buff.on(e.buff.duration)

        adv.Event("buff").listener(l_poised_buff)


ability_dict["poised"] = Poised_Buff


class Dodge_Buff(BuffingAbility):
    def __init__(self, name, value, duration=15, cooldown=15, cond=None):
        super().__init__(name, value, duration, cooldown)
        self.is_cd = False
        self.cond = cond

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return
        if not self.cond or adv.condition(f"dodge {self.cond}"):
            self.dodge_buff = adv.Buff(*self.buff_args, source="dodge")

            def l_dodge_buff(e):
                if not adv.is_set_cd(afrom, self.cooldown):
                    self.dodge_buff.on()

            adv.Event("dodge").listener(l_dodge_buff)


ability_dict["dodge"] = Dodge_Buff


class Healed_Buff(BuffingAbility):
    def __init__(self, name, value, duration=None, cooldown=None):
        super().__init__(name, value, duration or 15, cooldown or 10)

    def oninit(self, adv, afrom=None):
        if adv.nihilism:
            return

        def l_heal_buff(e):
            if not adv.is_set_cd(afrom, self.cooldown):
                adv.Buff(*self.buff_args, source="heal").on()

        adv.heal_event.listener(l_heal_buff)


ability_dict["healed"] = Healed_Buff


class Corrosion(Ability):
    def __init__(self, name, value):
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        self.getrecovery_mod = adv.Modifier("corrosion", "getrecovery", "buff", -0.5)
        self.set_hp_event = adv.Event("set_hp")
        self.set_hp_event.delta = -1
        self.set_hp_event.ignore_dragon = True
        self.set_hp_event.can_die = True
        self.set_hp_event.source = "dot"
        self.heal_to_reset = 3000

        def l_degen(t):
            self.set_hp_event.on()

        def l_amplify(t):
            self.set_hp_event.delta -= 1
            log("corrosion", "amplify", f"{self.set_hp_event.delta:+}%")

        def l_reset(e):
            self.heal_to_reset -= e.delta
            if self.heal_to_reset <= 0:
                self.set_hp_event.delta = -1
                self.heal_to_reset = 3000
                log("corrosion", "reset", f"{self.set_hp_event.delta:+}%")

        self.corrosion_degen = adv.Timer(l_degen, 2.9, True).on()
        self.corrosion_amplify = adv.Timer(l_amplify, 5, True).on()
        adv.heal_event.listener(l_reset)


ability_dict["corrosion"] = Corrosion


class CrisisPassive(Ability):
    def __init__(self, name, value):
        self.modtype = name.split("_")[-1]
        self.scale = value

    def oninit(self, adv, afrom=None):
        adv.crisis_mods[self.modtype].set_passive(self.scale)


ability_dict["crisis"] = CrisisPassive
