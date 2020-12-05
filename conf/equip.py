from conf import load_json, DURATION

BANNED_PRINTS = ('Witchs_Kitchen', 'Berry_Lovable_Friends', 'Happier_Times', 'United_by_One_Vision', 'Second_Anniversary')
ABNORMAL_COND = ('sim_buffbot', 'dragonbattle', 'classbane', 'hp', 'dumb', 'afflict_res', 'fleet')
BUFFER_TDPS_THRESHOLD = 40000
BUFFER_TEAM_THRESHOLD = 1.6
TDPS_WEIGHT = 15000

class EquipEntry(dict):
    CONF_KEYS = ('slots.a', 'slots.d', 'slots.w', 'acl', 'coabs', 'share')
    META_KEYS = ('dps', 'team')
    def __init__(self, adv, real_d, current=False):
        self.current = current
        self.eligablility(adv)
        ndps = sum(map(lambda v: sum(v.values()), adv.logs.damage.values())) / real_d
        nteam = adv.logs.team_buff / real_d
        new_equip = {
            'dps': ndps,
            'team': nteam,
            'tdps': None,
            'slots.a': adv.slots.a.qual_lst,
            'slots.d': adv.slots.d.qual,
        }
        if adv.slots.w.qual != adv.slots.DEFAULT_WEAPON:
            new_equip['slots.w'] = adv.slots.w.qual
        new_equip['acl'] = acl_list
        new_equip['coabs'] = adv.slots.c.coab_list
        new_equip['share'] = adv.skillshare_list
        super().__init__(new_equip)

    def eligablility(adv):
        adv.duration = int(adv.duration)
        if (adv.duration not in DURATION or \
            any([k in adv.conf for k in ABNORMAL_COND]) or \
            any([wp in BANNED_PRINTS for wp in adv.slots.a.qual_lst])):
            raise ValueError('build not eligable for equip')

    def same_build_different_dps(self, other):
        same_build = all((self.get(k) == other.get(k) for k in EquipEntry.CONF_KEYS))
        different_dps = any((self.get(k) != other.get(k) for k in EquipEntry.META_KEYS))

    @property
    def weighted(self):
        return self['dps'] + self['team'] * TDPS_WEIGHT

    def compare(self, other):
        """return (preferred, kicked)"""
        if current:
            if self.weighted > other.weighted:
                return self, other
            return other, self
        else:
            if self.weighted >= other.weighted:
                return self, other
            return other, self

    def update_threshold(self, other):
        if self['team'] != other['team']:
            self['tdps'] = (self['dps'] - other['dps']) / (other['team'] - self['team'])
            other['tdps'] = -self['tdps']
        else:
            self['team'] = None
            other['tdps'] = None