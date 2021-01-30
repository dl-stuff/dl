from core.afflic import AFFLICT_LIST
from conf import ELEMENTS, WEAPON_TYPES

class Ability:
    def __init__(self, name, mod=None):
        self.name = name
        self.mod = mod or []

    def check_ele_wt(self, m, adv):
        cond = m[3]
        if '_' in cond:
            classifier, cond = cond.split('_')
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

    def flurry_modifier(self, m, adv):
        cond = m[3]
        if cond.startswith('hit'):
            flurry_hits = int(cond[3:])
            def flurry_get():
                return adv.hits > flurry_hits
            adv.uses_combo = True
            return (m[0], m[1], m[2], cond, flurry_get)
        return m

    def oninit(self, adv, afrom=None):
        if afrom is not None:
            afrom += '_'
        else:
            afrom = ''
        for idx, m in enumerate(self.mod):
            if len(m) > 3 and m[3] is not None:
                is_ele_wt, m = self.check_ele_wt(m, adv)
                if not is_ele_wt:
                    continue
                if m[3] is not None:
                    m = self.flurry_modifier(m, adv)
            mod_name = '{}{}_{}'.format(afrom, self.name, idx)
            self.mod_object = adv.Modifier(mod_name,*m)
            if m[1] == 'buff':
                adv.Buff(f'{mod_name}_buff', duration=-1, modifier=self.mod_object, source='ability').on()

ability_dict = {}

class Strength(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('att', 'passive', value, cond)])
ability_dict['a'] = Strength
ability_dict['au'] = Strength # united strength

class Strength_Chain(Ability):
    def __init__(self, name, value, cond=None):
        # is buff bracket for some hecking reason
        super().__init__(name, [('att','buff',value, cond)])
ability_dict['achain'] = Strength_Chain

class Resist(Ability):
    def __init__(self, name, value, cond=None):
        if not cond or cond.startswith('hp'):
            super().__init__(name, [(name,'passive',value, cond)])
        else:
            super().__init__(name, [(name,'buff',value, cond)])
ability_dict['res'] = Resist


class Skill_Damage(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('s','passive',value, cond)])
ability_dict['s'] = Skill_Damage
ability_dict['sd'] = Skill_Damage


class Force_Strike(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('fs','passive',value, cond)])
ability_dict['fs'] = Force_Strike


class Health_Points(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('maxhp','passive',value, cond)])
ability_dict['hp'] = Health_Points


class Buff_Time(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('buff','passive',value, cond)])
ability_dict['bt'] = Buff_Time


class Debuff_Time(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('debuff','passive',value, cond)])
ability_dict['dbt'] = Debuff_Time

class ConditionalModifierAbility(Ability):
    def __init__(self, name, mtype, morder, value, cond=None):
        if '_' in name:
            afflict = name.split('_', 1)[1]
            super().__init__(name, [(f'{afflict}_{mtype}', morder, value, cond)])
        else:
            super().__init__(name, [(mtype, morder, value, cond)])

class Critical_Chance(ConditionalModifierAbility):
    def __init__(self, name, value, cond=None):
        super().__init__(name, 'crit','chance', value, cond)

ability_dict['cc'] = Critical_Chance


class Critical_Damage(ConditionalModifierAbility):
    def __init__(self, name, value, cond=None):
        super().__init__(name, 'crit','damage',value, cond)

ability_dict['cd'] = Critical_Damage


class Killer(ConditionalModifierAbility):
    def __init__(self, name, value, cond=None):
        super().__init__(name, 'killer','passive',value, cond)
ability_dict['k'] = Killer


class Skill_Haste(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('sp', 'passive', value, cond)])
ability_dict['sp'] = Skill_Haste
ability_dict['spu'] = Skill_Haste # united haste


class Striking_Haste(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('spf', 'passive', value, cond)])
ability_dict['spf'] = Striking_Haste


class Broken_Punisher(Ability):
    EFFICIENCY = 0.15
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('att', 'bk', value*self.EFFICIENCY, cond)])
    
    def oninit(self, adv, afrom=None):
        if not adv.conf['berserk']:
            super().oninit(adv, afrom=afrom)
ability_dict['bk'] = Broken_Punisher


class Overdrive_Punisher(Ability):
    EFFICIENCY = 0.45
    def __init__(self, name, value, cond=None):
        self.value = value
        self.cond = cond
        super().__init__(name, [('killer','passive',value, cond)])

    def oninit(self, adv, afrom=None):
        if not adv.conf['berserk']:
            self.mod = [('killer', 'passive', self.value*self.EFFICIENCY, self.cond)]
        super().oninit(adv, afrom=afrom)
ability_dict['od'] = Overdrive_Punisher


class Gauge_Accelerator(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('odaccel', 'passive', value, cond)])
ability_dict['odaccel'] = Overdrive_Punisher


class Dragon_Damage(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('da','passive',value,cond)])
ability_dict['da'] = Dragon_Damage


class Dragon_Time(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('dt','passive',value,cond)])
ability_dict['dt'] = Dragon_Time


class Dragon_Haste(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('dh','passive',value,cond)])
ability_dict['dh'] = Dragon_Haste


class Attack_Speed(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('spd','passive',value, cond)])
ability_dict['spd'] = Attack_Speed


class Charge_Speed(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('cspd','passive',value, cond)])
ability_dict['cspd'] = Charge_Speed


class Combo_Time(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('ctime','passive',value, cond)])
ability_dict['ctime'] = Combo_Time


class Bleed_Killer(Ability):
    def __init__(self, name, value, cond=None):
        super().__init__(name, [('killer','passive',value, cond)])

    def oninit(self, adv, afrom=None):
        super().oninit(adv, afrom=afrom)
        value = self.mod_object.get()
        def get_bleed():
            try:
                return value if adv.bleed.get() > 0 else 0
            except AttributeError:
                return 0
        self.mod_object.get = get_bleed
ability_dict['bleed'] = Bleed_Killer


class Co_Ability(Ability):
    EX_MAP = {
        'blade': [('att','ex',0.10)],
        'dagger': [('crit','chance',0.10)],
        'bow': [('sp','passive',0.15)],
        'wand': [('s','ex',0.15)],
        'sword': [('dh','passive',0.15)],
        'axe2': [('crit','damage',0.30)],
        'dagger2': [('x','ex',0.20)],
        'gun': [('odaccel', 'passive', 0.20)],
        'geuden': [('da','passive',0.10), ('dt','passive',0.20)],
        'megaman': [('killer','passive',0.15*Overdrive_Punisher.EFFICIENCY), ('odaccel', 'passive', 0.10)],
        'tobias': [('buff','ex',0.20)],
        'grace': [('fs','ex',0.20)],
        'sharena': [('paralysis_killer', 'passive', 0.08)],
        'peony': [('light','ele',0.20)],
        'gleif': [('debuff_killer', 'passive', 0.08)]
    }
    def __init__(self, name, value):
        self.coab_type = value
        super().__init__(name, self.EX_MAP[value])

    def oninit(self, adv, afrom=None):
        if adv.conf['berserk'] and self.coab_type == 'megaman':
            self.mod = [('killer','passive',0.15), ('odaccel', 'passive', 0.10)]
        super().oninit(adv, afrom=afrom)

ability_dict['ex'] = Co_Ability


class Union_Ability(Ability):
    UNION_MAP = {
        1: {4: [('s', 'passive', 0.10)]},
        2: {4: [('att','bk', 0.10*Broken_Punisher.EFFICIENCY)]},
        3: {4: [('att','passive', 0.08)]},
        4: {3: [('sp','passive', 0.06)], 4: [('sp','passive', 0.10)]},
        5: {2: [('da','passive', 0.10)], 3: [('da','passive', 0.18)], 4: [('da','passive', 0.30)]},
        6: {2: [('fs','passive', 0.05)], 3: [('fs','passive', 0.08)], 4: [('fs','passive', 0.15)]},
        # 7: burn res, 8: stun res, 9: para res, 10: curse res
        11: {2: [('buff','passive', 0.05)], 3: [('buff','passive', 0.08)], 4: [('buff','passive', 0.15)]},
    }
    def __init__(self, name, value, level):
        self.union_id = value
        self.union_lv = level
        super().__init__(name, self.UNION_MAP[value][level].copy())

    def oninit(self, adv, afrom=None):
        if not adv.conf['berserk'] or not (self.union_id == 3 and self.union_lv >= 4):
            super().oninit(adv, afrom=afrom)
ability_dict['union'] = Union_Ability


class BuffingAbility(Ability):
    def __init__(self, name, value, duration):
        self.buff_args = (name, value, duration, 'att', 'buff')
        if '_' in name:
            # how dum
            extra_args = (arg.replace('-', '_') for arg in name.split('_')[1:])
            self.buff_args = (name, value, duration, *extra_args)
        super().__init__(name)

class Last_Buff(BuffingAbility):
    HEAL_TO = 30
    def __init__(self, name, value, duration=15, chances=1):
        super().__init__(name, value, duration)
        self.proc_chances = chances
        self.auto_proc = 'regen' not in self.buff_args
        Last_Buff.HEAL_TO = 30

    def oninit(self, adv, afrom=None):
        def l_lo_buff(e):
            if self.proc_chances > 0 and e.hp <= 30 and (e.hp - e.delta) > 30:
                self.proc_chances -= 1
                adv.Buff(*self.buff_args).no_bufftime().on()
        adv.Event('hp').listener(l_lo_buff)
        if self.auto_proc and 'hp' not in adv.conf and adv.condition('last offense'):
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

ability_dict['lo'] = Last_Buff


class Doublebuff(BuffingAbility):
    def __init__(self, name, value, duration=15):
        super().__init__(name, value, duration)

    def oninit(self, adv, afrom=None):
        if self.name == 'bc_energy':
            def defchain(e):
                if hasattr(e, 'rate'):
                    adv.energy.add(self.buff_args[1] * e.rate)
                else:
                    adv.energy.add(self.buff_args[1])
            adv.Event('defchain').listener(defchain)
        else:
            def defchain(e):
                if hasattr(e, 'rate'):
                    adv.Buff(self.buff_args[0], self.buff_args[1] * e.rate, *self.buff_args[2:], source=e.source).on()
                else:
                    adv.Buff(*self.buff_args, source=e.source).on()
            adv.Event('defchain').listener(defchain)

ability_dict['bc'] = Doublebuff


class Doublebuff_CD(Doublebuff):
    DB_CD = 14.999 # inaccurate, but avoids a potential unintuitive race condition
    def oninit(self, adv, afrom=None):
        self.is_cd = False

        def cd_end(t):
            self.is_cd = False

        if self.name == 'bcc_energy':
            def defchain(e):
                if not self.is_cd:
                    adv.energy.add(self.buff_args[1])
                    self.is_cd = True
                    adv.Timer(cd_end).on(self.DB_CD)
            adv.Event('defchain').listener(defchain)
        else:
            def defchain(e):
                if not self.is_cd:
                    adv.Buff(*self.buff_args, source=e.source).on()
                    self.is_cd = True
                    adv.Timer(cd_end).on(self.DB_CD)
            adv.Event('defchain').listener(defchain)

ability_dict['bcc'] = Doublebuff_CD


class Slayer_Strength(BuffingAbility):
    def __init__(self, name, value):
        super().__init__(name, value, -1)

    def oninit(self, adv, afrom=None):
        pass
        # for _ in range(5):
        #     adv.Buff(*self.buff_args).on()

ability_dict['sts'] = Slayer_Strength
ability_dict['sls'] = Slayer_Strength


class Dragon_Buff(Ability):
    def __init__(self, name, dc_values, buff_args=()):
        self.dc_values = dc_values
        self.buff_args = buff_args
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        self.dc_level = 0
        def l_dc_buff(t):
            if self.dc_level < len(self.dc_values):
                adv.Buff(self.name, self.dc_values[self.dc_level], -1, *self.buff_args).on()
                self.dc_level += 1
        adv.Event('dragon').listener(l_dc_buff)

class Dragon_Claw(Dragon_Buff):
    DC_LEVELS = {
        1: (0.04,0.06,0.10),
        2: (0.05,0.08,0.12),
        3: (0.06,0.09,0.15),
        4: (0.10,0.15,0.15)
    }
    def __init__(self, name, value):
        super().__init__('dca', self.DC_LEVELS[value])

ability_dict['dc'] = Dragon_Claw

class Dragon_Might(Dragon_Buff):
    DM_LEVELS = {
        1: (0.10, 0.10)
    }
    def __init__(self, name, value):
        super().__init__('dca', self.DM_LEVELS[value])

ability_dict['dm'] = Dragon_Might

class Dragon_Claw_Chain(Dragon_Buff):
    DCC_LEVELS = {
        3: (0.08, 0.09, 0.15),
        5: (0.09, 0.10, 0.15),
        6: (0.10, 0.10, 0.15)
    }
    def __init__(self, name, value):
        super().__init__('dca', self.DCC_LEVELS[value])

ability_dict['dcc'] = Dragon_Claw_Chain

class Dragon_Skill(Dragon_Buff):
    DS_LEVELS = {
        3: (0.08, 0.08, 0.08)
    }
    def __init__(self, name, value):
        super().__init__('dcs', self.DS_LEVELS[value], buff_args=('s','buff'))

ability_dict['dcs'] = Dragon_Skill

class Dragon_Scale(Dragon_Buff):
    DD_LEVELS = {
        3: (0.10, 0.11, 0.12)
    }
    def __init__(self, name, value):
        super().__init__('dcd', self.DD_LEVELS[value], buff_args=('defense','buff'))

ability_dict['dcd'] = Dragon_Scale

class Resilient_Offense(BuffingAbility):
    def __init__(self, name, value, interval=None):
        super().__init__(name, value, -1)
        self.interval = interval
        if name[0:2] == 'ro':
            self.proc_chances = 3
            self.hp_threshold = 30
        elif name[0:2] == 'uo':
            self.proc_chances = 5
            self.hp_threshold = 70

    def oninit(self, adv, afrom=None):
        def l_ro_buff(e):
            if self.proc_chances > 0 and e.hp <= 30 and (e.hp - e.delta) > 30:
                self.proc_chances -= 1
                adv.Buff(*self.buff_args).on()
        adv.Event('hp').listener(l_ro_buff)
        if self.interval and 'hp' not in adv.conf:
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
            if self.interval < adv.duration and adv.condition(f'hp={self.hp_threshold}% every {self.interval}s'):
                for i in range(1, self.proc_chances):
                    adv.Timer(ro_damaged).on(self.interval*i)
            adv.Timer(ro_damaged).on(0.1)

ability_dict['ro'] = Resilient_Offense
ability_dict['uo'] = Resilient_Offense


class Skill_Prep(Ability):
    def __init__(self, name, value, cond=None):
        self.value = value
        if isinstance(self.value, str):
            self.value = float(value.replace('%', ''))
        if self.value > 1:
            self.value /= 100
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        adv.charge_p('skill_prep',self.value)

ability_dict['prep'] = Skill_Prep


class Primed(BuffingAbility):
    PRIMED_CD = 14.999
    def __init__(self, name, value, duration=None):
        self.is_cd = False
        super().__init__(name, value, duration or 10)

    def oninit(self, adv, afrom=None):
        def pm_cd_end(t):
            self.is_cd = False

        primed_buff = adv.Buff(*self.buff_args).no_bufftime()
        def l_primed(e):
            if not self.is_cd:
                primed_buff.on()
                self.is_cd = True
                adv.Timer(pm_cd_end).on(self.PRIMED_CD)

        adv.Event('s1_charged').listener(l_primed)

ability_dict['primed'] = Primed


class Dragon_Prep(Ability):
    def __init__(self, name, value):
        self.value = value
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        adv.dragonform.charge_gauge(self.value * 10, dhaste=False)

ability_dict['dp'] = Dragon_Prep


class Affliction_Guard(Ability):
    def __init__(self, name, value):
        self.value = value
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        adv.afflict_guard = self.value
        adv.dragonform.disabled = False

ability_dict['ag'] = Affliction_Guard

class Energy_Prep(Ability):
    def __init__(self, name, value):
        self.energy_count = value
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        adv.energy.add(self.energy_count)

ability_dict['eprep'] = Energy_Prep


class Force_Charge(Ability):
    def __init__(self, name, charge, value=0.25):
        self.charge = charge
        self.value = value
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        if hasattr(adv, 'fs_prep_c'):
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
            self.l_fs_charge = adv.Listener('fs-h', l_fs_charge)

            i = 1
            fsi = f'fs{i}'
            while hasattr(adv, fsi):
                self.l_fs_charge = adv.Listener(fsi, l_fs_charge)
                i += 1
                fsi = f'fs{i}'
            adv.fs_prep_c = self.charge
            adv.fs_prep_v = self.value

ability_dict['fsprep'] = Force_Charge


class Energized_Buff(BuffingAbility):
    def __init__(self, name, value, duration=None):
        super().__init__(name, value, duration or 15)

    def oninit(self, adv, afrom=None):
        def l_energized(e):
            if e.stack >= 5:
                adv.Buff(*self.buff_args).on()

        adv.Event('energy').listener(l_energized)

ability_dict['energized'] = Energized_Buff


class Energy_Buff(BuffingAbility):
    E_CD = 14.999
    def __init__(self, name, value, duration=None):
        super().__init__(name, value, duration or 15)
        self.is_cd = False

    def oninit(self, adv, afrom=None):
        def cd_end(t):
            self.is_cd = False
        if self.name == 'energy_inspiration':
            def l_energy(e):
                if not self.is_cd:
                    adv.inspiration.add(self.buff_args[1])
                    self.is_cd = True
                    adv.Timer(cd_end).on(self.E_CD)
        else:
            def l_energy(e):
                if not self.is_cd:
                    adv.Buff(*self.buff_args).on()
                    self.is_cd = True
                    adv.Timer(cd_end).on(self.E_CD)

        adv.Event('energy').listener(l_energy)

ability_dict['energy'] = Energy_Buff


class Affliction_Selfbuff(Ability):
    def __init__(self, name, value, duration=15, cd=10, is_rng=False):
        nameparts = name.split('_')
        self.atype = nameparts[1].strip()
        self.value = value
        self.duration = duration
        self.buff_args = nameparts[2:]
        self.cd = cd - 0.001
        self.is_rng = is_rng
        self.is_cd = False
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        def cd_end(t):
            self.is_cd = False
        def l_afflict(e):
            if not self.is_cd:
                if self.is_rng:
                    import random
                    if random.random() < e.rate:
                        adv.Buff(self.name, self.value, self.duration, *self.buff_args, source=e.source).on()
                        self.is_cd = True
                        adv.Timer(cd_end).on(self.cd)
                else:
                    adv.Buff(self.name, self.value * e.rate, self.duration, *self.buff_args, source=e.source).on()
                    self.is_cd = True
                    adv.Timer(cd_end).on(self.cd)
        adv.Event(self.atype).listener(l_afflict)

ability_dict['affself'] = Affliction_Selfbuff


class Affliction_Teambuff(Affliction_Selfbuff):
    def oninit(self, adv, afrom=None):
        def cd_end(t):
            self.is_cd = False
        def l_afflict(e):
            if not self.is_cd and e.rate > 0:
                adv.Teambuff(self.name, self.value * e.rate, self.duration, *self.buff_args, source=e.source).on()
                self.is_cd = True
                adv.Timer(cd_end).on(self.cd)
        adv.Event(self.atype).listener(l_afflict)

ability_dict['affteam'] = Affliction_Teambuff


class AntiAffliction_Selfbuff(Affliction_Selfbuff):
    def oninit(self, adv, afrom=None):
        def cd_end(t):
            self.is_cd = False
        def l_afflict(e):
            if not self.is_cd and e.rate < 1:
                adv.Buff(self.name, self.value * (1 - e.rate), self.duration, *self.buff_args, source=e.source).on()
                self.is_cd = True
                adv.Timer(cd_end).on(self.cd)
        adv.Event(self.atype).listener(l_afflict)

ability_dict['antiaffself'] = AntiAffliction_Selfbuff


class Energy_Stat(Ability):
    STAT_LEVELS = {
        ('att', 'passive'): {
            3: (0.0, 0.04, 0.06, 0.08, 0.10, 0.20),
            7: (0.0, 0.05, 0.10, 0.20, 0.30, 0.40),
            'chariot': (0.0, 0.25, 0.30, 0.35, 0.40, 0.45)
        },
        ('crit', 'chance'): {
            3: (0.0, 0.01, 0.02, 0.03, 0.04, 0.08),
            7: (0.0, 0.01, 0.04, 0.07, 0.10, 0.15)
        },
        ('sp', 'passive'): {
            3: (0.0, 0.05, 0.10, 0.15, 0.20, 0.25),
        }
    }
    def __init__(self, name, value):
        parts = name.split('_')
        self.mtype = parts[1]
        try:
            self.morder = parts[2]
        except IndexError:
            self.morder = 'chance' if self.mtype == 'crit' else 'passive'
        self.stat_values = Energy_Stat.STAT_LEVELS[(self.mtype, self.morder)][value]
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        from core.advbase import log
        stat_mod = adv.Modifier(self.name, self.mtype, self.morder, 0.0)
        def l_energy(e):
            stat_mod.mod_value = self.stat_values[round(adv.energy.stack)]
            log(self.name, stat_mod.mod_value, adv.energy.stack)
        adv.Event('energy').listener(l_energy)
        adv.Event('energy_end').listener(l_energy)

ability_dict['estat'] = Energy_Stat


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
        self.haste_buff = adv.Selfbuff('ehaste', 0.00,-1,'sp', 'passive').on()
        def l_energy(e):
            self.haste_buff.off()
            self.haste_buff.set(self.haste_values[round(e.stack)])
            self.haste_buff.on()
        adv.Event('energy').listener(l_energy)

ability_dict['ehaste'] = Energy_Stat


class Affliction_Edge(Ability):
    def __init__(self, name, value, cond=None):
        self.atype = name.split('_')[1]
        super().__init__(name, [('edge', self.atype, value, cond)])

    def oninit(self, adv, afrom=None):
        super().oninit(adv, afrom)
        adv.afflics.__dict__[self.atype].aff_edge_mods.append(self.mod_object)

ability_dict['edge'] = Affliction_Edge


class ComboProcAbility(Ability):
    def __init__(self, name, value, cond=None):
        self.threshold = value
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        if adv.condition('always connect hits'):
            self.add_combo_o = adv.add_combo
            self.ehit = 0
            def add_combo(name='#'):
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
        raise NotImplementedError('combo_proc_cb')

    def combo_reset_cb(self):
        pass

class Energy_Combo(ComboProcAbility):
    def combo_proc_cb(self, adv, delta):
        adv.energy.add(delta)

ability_dict['ecombo'] = Energy_Combo


class DPrep_Combo(ComboProcAbility):
    def combo_proc_cb(self, adv, delta):
        adv.dragonform.charge_gauge(delta*30, dhaste=False)

ability_dict['dpcombo'] = DPrep_Combo


class Crit_Combo_Resetable(ComboProcAbility):
    def oninit(self, adv, afrom=None):
        super().oninit(adv, afrom=afrom)
        self.combo_crit_mod = adv.Modifier(self.name, 'crit', 'chance', 0.0)

    def combo_proc_cb(self, adv, delta):
        self.combo_crit_mod.mod_value = min(0.20, (adv.hits // self.threshold) * 0.01)

    def combo_reset_cb(self):
        self.combo_crit_mod.mod_value = 0

ability_dict['critcombo'] = Crit_Combo_Resetable


class Skill_Recharge(Ability):
    def __init__(self, name, value):
        self.all = name == 'scharge_all'
        self.value = value
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        if self.all:
            def l_skill_charge(e):
                adv.charge_p('scharge',self.value)
        else:
            def l_skill_charge(e):
                try:
                    adv.charge_p('scharge',self.value,target=e.base)
                except AttributeError:
                    pass
        adv.Event('s').listener(l_skill_charge)

ability_dict['scharge'] = Skill_Recharge


class Crisis_Att_Spd(Ability):
    BUFF_LEVEL = {
        2: (0.15, 0.10),
        3: (0.20, 0.10)
    }
    def __init__(self, name, lvl):
        self.att, self.spd = Crisis_Att_Spd.BUFF_LEVEL[lvl]
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        from core.advbase import Selfbuff, Spdbuff
        self.atk_buff = Selfbuff(f'{self.name}_att',self.att,-1,'att','passive')
        self.spd_buff = Spdbuff(f'{self.name}_spd',self.spd,-1)
        def l_cas_buff(e):
            if e.hp <= 30:
                self.atk_buff.on()
                self.spd_buff.on()
            else:
                self.atk_buff.off()
                self.spd_buff.off()
        adv.Event('hp').listener(l_cas_buff)

ability_dict['crisisattspd'] = Crisis_Att_Spd

class Energy_Extra(Ability):
    def __init__(self, name, value, rng=False):
        self.use_rng = rng
        self.value = value
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        if self.use_rng:
            def l_energy(e):
                import random
                if random.random() < self.value:
                    adv.energy.add_extra(1)
        else:
            def l_energy(e):
                adv.energy.add_extra(self.value) # means

        adv.Event('energy').listener(l_energy)

ability_dict['eextra'] = Energy_Extra


class Damaged_Buff(BuffingAbility):
    def oninit(self, adv, afrom=None):
        from core.modifier import SingleActionBuff
        if self.buff_args[1] == 'fs':
            self.damaged_buff = SingleActionBuff(*self.buff_args)
            def l_damaged_buff(e):
                if e.delta < 0:
                    self.damaged_buff.on()
        else:
            self.is_cd = False
            def cd_end(t):
                self.is_cd = False
            def l_damaged_buff(e):
                if not self.is_cd and e.delta < 0:
                    adv.Buff(*self.buff_args).on()
                    self.is_cd = True
                    adv.Timer(cd_end).on(5) # ycass
        adv.Event('hp').listener(l_damaged_buff)
ability_dict['damaged'] = Damaged_Buff


class Poised_Buff(Ability):
    def __init__(self, name, value, passive=False):
        self.value = value
        self.buff_args = (arg.replace('-', '_') for arg in name.split('_')[1:])
        self.passive = passive
        super().__init__(name)

    def oninit(self, adv, afrom=None):
        from core.modifier import ZoneTeambuff
        self.poised_buff = adv.Buff(self.name, self.value, -1, *self.buff_args)
        if self.passive:
            self.poised_buff.hidden = True
        def l_poised_buff(e):
            if isinstance(e.buff, ZoneTeambuff):
                self.poised_buff.on(e.buff.duration)
        adv.Event('buff').listener(l_poised_buff)

ability_dict['poised'] = Poised_Buff


class Dodge_Buff(BuffingAbility):
    D_CD = 14.999
    def __init__(self, name, value, duration=None):
        super().__init__(name, value, duration or 15)
        self.is_cd = False

    def oninit(self, adv, afrom=None):
        def cd_end(t):
            self.is_cd = False
        def l_dodge_buff(e):
            if not self.is_cd:
                adv.Buff(*self.buff_args, source='dodge').on()
                self.is_cd = True
                adv.Timer(cd_end).on(self.D_CD)
        adv.Event('dodge').listener(l_dodge_buff)

ability_dict['dodge'] = Dodge_Buff
