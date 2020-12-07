from pprint import pprint
from copy import deepcopy

from conf import load_json, save_json, DURATIONS, ELE_AFFLICT, mono_elecoabs, load_adv_json
import core.simulate

BANNED_PRINTS = ('Witchs_Kitchen', 'Berry_Lovable_Friends', 'Happier_Times', 'United_by_One_Vision', 'Second_Anniversary')
ABNORMAL_COND = ('sim_buffbot', 'dragonbattle', 'classbane', 'hp', 'dumb', 'afflict_res', 'fleet')
BUFFER_TDPS_THRESHOLD = 40000
BUFFER_TEAM_THRESHOLD = 1.6
TDPS_WEIGHT = 15000

class EquipEntry(dict):
    CONF_KEYS = ('slots.a', 'slots.d', 'slots.w', 'acl', 'coabs', 'share')
    META_KEYS = ('dps', 'team')

    def __init__(self, equip):
        super().__init__(equip)

    @staticmethod
    def eligible(adv):
        adv.duration = int(adv.duration)
        return (adv.duration in DURATIONS and \
            all([not k in adv.conf for k in ABNORMAL_COND]) or \
            all([not wp in BANNED_PRINTS for wp in adv.slots.a.qual_lst]))

    @staticmethod
    def acceptable(entry, ele=None):
        return isinstance(entry, EquipEntry)

    def same_build_different_dps(self, other):
        same_build = all((self.get(k) == other.get(k) for k in EquipEntry.CONF_KEYS))
        different_dps = any((self.get(k) != other.get(k) for k in EquipEntry.META_KEYS))

    @staticmethod
    def weight(entry):
        return entry['dps'] + entry['team'] * TDPS_WEIGHT

    def better_than(self, other):
        return self.weight(self) > self.weight(other)

    def update_threshold(self, other):
        if self['team'] != other['team']:
            self['tdps'] = None
            other['tdps'] = (self['dps'] - other['dps']) / (other['team'] - self['team'])
        else:
            self['tdps'] = None
            other['tdps'] = None

def build_entry_from_sim(entryclass, adv, real_d):
    ndps = sum(map(lambda v: sum(v.values()), adv.logs.damage.values())) / real_d
    nteam = adv.logs.team_buff / real_d
    new_equip = {
        'dps': ndps,
        'team': nteam,
        'tdps': None,
        'ele': adv.slots.c.ele,
        'slots.a': adv.slots.a.qual_lst
    }
    if adv.slots.d.qual != adv.slots.DEFAULT_DRAGON[adv.slots.c.ele]:
        new_equip['slots.d'] = adv.slots.d.qual
    if adv.slots.w.qual != adv.slots.DEFAULT_WEAPON:
        new_equip['slots.w'] = adv.slots.w.qual
    acl_list = adv.conf.acl
    if not isinstance(acl_list, list):
        acl_list = [line.strip() for line in acl_list.split('\n') if line.strip()]
    new_equip['acl'] = acl_list
    new_equip['coabs'] = adv.slots.c.coab_list
    new_equip['share'] = adv.skillshare_list
    return entryclass(new_equip)

class BaseEntry(EquipEntry):
    @staticmethod
    def eligible(adv):
        return not adv.sim_afflict and EquipEntry.eligible(adv)

class BufferEntry(EquipEntry):
    @staticmethod
    def acceptable(entry, ele=None):
        return entry['team'] and EquipEntry.acceptable(entry)

    def better_than(self, other):
        return self['team'] > other['team'] or self['dps'] > other['dps']

class AfflictionEntry(EquipEntry):
    @staticmethod
    def eligible(adv):
        eleaff = ELE_AFFLICT[adv.slots.c.ele]
        return (adv.sim_afflict == {eleaff} and adv.conf_init.sim_afflict[eleaff] == 1) and EquipEntry.eligible(adv)

def all_monoele_coabs(entry, ele):
    return all((coab in mono_elecoabs[ele] for coab in entry['coabs']))

class MonoBaseEntry(BaseEntry):
    @staticmethod
    def acceptable(entry, ele):
        return all_monoele_coabs(entry, ele) and BaseEntry.acceptable(entry)

class MonoBufferEntry(BufferEntry):
    @staticmethod
    def acceptable(entry, ele):
        return all_monoele_coabs(entry, ele) and BufferEntry.acceptable(entry)

class MonoAfflictionEntry(AfflictionEntry):
    @staticmethod
    def acceptable(entry, ele):
        return all_monoele_coabs(entry, ele) and AfflictionEntry.acceptable(entry)

EQUIP_ENTRY_MAP = {
    'base': BaseEntry,
    'buffer': BufferEntry,
    'affliction': AfflictionEntry,
    # 'affbuff' ?
    'mono_base': MonoBaseEntry,
    'mono_buffer': MonoBufferEntry,
    'mono_affliction': MonoAfflictionEntry
}
KICK_TO = {
    'base': ('buffer', 'mono_base'),
    'buffer': ('base', 'mono_buffer'),
    'affliction': ('mono_affliction',)
}
THRESHOLD_RELATION = (
    ('base', 'buffer', 'pref'),
    ('mono_base', 'mono_buffer', 'mono_pref'),
)


class EquipManager(dict):
    def __init__(self, advname, debug=False):
        self.advname = advname
        if debug:
            super().__init__({})
            self.debug = True
        else:
            super().__init__(load_json(f'equip/{advname}.json'))
            self.debug = False
        self.pref = None
        for duration, dequip in self.items():
            for kind, entry in dequip:
                try:
                    dequip[kind] = EQUIP_ENTRY_MAP[kind](entry)
                except KeyError:
                    if kind == 'pref':
                        self.pref = entry

    def accept_new_entry(self, adv, real_d):
        if self.advname != adv.name:
            raise RuntimeError(f'adv/equip name mismatch {self.advname} != {adv.name}')

        duration = str(adv.duration)
        kicked_entries = []
        need_write = False
        if duration not in self:
            self[duration] = {'pref': 'base', 'mono_pref': 'mono_base'}

        # first pass
        for kind, entryclass in EQUIP_ENTRY_MAP.items():
            if not entryclass.eligible(adv):
                continue
            new_entry = build_entry_from_sim(entryclass, adv, real_d)
            if not entryclass.acceptable(new_entry, adv.slots.c.ele):
                continue
            try:
                current_entry = self[duration][kind]
            except KeyError:
                self[duration][kind] = new_entry
                continue
            keep, kicked = current_entry, new_entry
            if current_entry.same_build_different_dps(new_entry) or not current_entry.better_than(new_entry):
                keep, kicked = new_entry, current_entry
                need_write = True
            self[duration][kind] = keep
            try:
                for kicked_kind in KICK_TO[kind]:
                    kicked_entries.append((kicked_kind, kicked))
            except KeyError:
                pass

        # kicked entries
        for kind, kicked in kicked_entries:
            entryclass = EQUIP_ENTRY_MAP[kind]
            if not entryclass.acceptable(kicked, adv.slots.c.ele):
                continue
            kicked = entryclass(kicked)
            try:
                current_entry = self[duration][kind]
            except KeyError:
                self[duration][kind] = kicked
                continue
            if not current_entry.better_than(kicked):
                self[duration][kind] = kicked

        # tdps threshold
        for basekind, buffkind, prefkey in THRESHOLD_RELATION:
            try:
                self[duration][basekind].update_threshold(self[duration][buffkind])
                try:
                    if (self[duration][buffkind]['team'] > BUFFER_TEAM_THRESHOLD or
                        self[duration][buffkind]['tdps'] < BUFFER_TDPS_THRESHOLD):
                        self[duration][prefkey] = buffkind
                except TypeError:
                    self[duration][prefkey] = basekind
            except KeyError:
                continue

        if self.debug:
            print('~'*60)
            pprint(self)
            print('~'*60)
        elif need_write:
            save_json(f'equip/{self.advname}.json', self, indent=2)

    def repair_entry(self, adv_module, element, conf, duration, kind):
        conf = deepcopy(conf)
        if kind in ('affliction', 'mono_affliction'):
            conf['sim_afflict'][ELE_AFFLICT[element]] = 1
        run_res = core.simulate.test(self.advname, adv_module, conf, int(duration))
        adv = run_res[0][0]
        real_d = run_res[0][1]
        self.accept_new_entry(adv, real_d)

    def repair_entries(self):
        adv_module, _ = core.simulate.load_adv_module(self.advname)
        element = load_adv_json(self.advname)['c']['ele']
        for duration in self:
            for kind in self[duration]:
                if kind.startswith('pref'):
                    continue
                self.repair_entry(adv_module, element, self[duration][kind], duration, kind)
                if duration != '180':
                    try:
                        self.repair_entry(adv_module, element, self['180'][kind], duration, kind)
                    except KeyError:
                        pass
                for affkind, basekind in (('affliction', 'base'), ('mono_affliction', 'mono_base')):
                    try:
                        self.repair_entry(adv_module, element, self[duration][basekind], duration, affkind)
                    except KeyError:
                        pass

def _test_equip(advname, confs):
    adv_module, advname = core.simulate.load_adv_module(advname)
    equip_manager = EquipManager(advname, debug=True)
    for conf in confs:
        run_res = core.simulate.test(advname, adv_module, conf, 180)
        adv = run_res[0][0]
        real_d = run_res[0][1]
        equip_manager.accept_new_entry(adv, real_d)
    return equip_manager

def test_equip_simple():
    basic_conf = {
        'slots.a': [
            'Candy_Couriers',
            'Me_and_My_Bestie',
            'Memory_of_a_Friend',
            'The_Plaguebringer',
            'To_the_Extreme'
        ],
        'slots.d': 'Gala_Mars',
        'acl': [
            '`dragon(s-s)',
            '`s3, not buff(s3) and x=5',
            '`s1',
            '`s4,cancel',
            '`s2, x=5'
        ],
        'coabs': [
            'Blade',
            'Joe',
            'Marth'
        ],
        'share': [
            'Weapon',
            'Durant'
        ]
    }
    higher_team_conf = {
        **basic_conf,
        'share': [
            'Weapon',
            'Karl'
        ]
    }
    higher_dps_conf = {
        **basic_conf,
        'share': [
            'Weapon',
            'Formal_Joachim'
        ]
    }
    _test_equip('Xania', (basic_conf, higher_team_conf))

def test_equip_afflictions():
    basic_conf = {
      "slots.a": [
        "An_Ancient_Oath",
        "Dragon_and_Tamer",
        "Memory_of_a_Friend",
        "Entwined_Flames",
        "The_Plaguebringer"
      ],
      "slots.d": "Gala_Cat_Sith",
      "acl": [
        "`fs, x=5",
        "`s3, not buff(s3)",
        "`s2",
        "`s4",
        "`dragon(c3-s-end), cancel",
        "`s1(all)"
      ],
      "coabs": [
        "Ieyasu",
        "Wand",
        "Forte"
      ],
      "share": [
        "Weapon",
        "Gala_Mym"
      ]
    }
    basic_on_conf = {
        **basic_conf,
        'sim_afflict': {'poison': 1}
    }
    afflic_conf = {
      "slots.a": [
        "An_Ancient_Oath",
        "Dragon_and_Tamer",
        "Memory_of_a_Friend",
        "Dueling_Dancers",
        "The_Plaguebringer"
      ],
      "slots.d": "Gala_Cat_Sith",
      "acl": [
        "`dragon(c3-s-end), s4",
        "`s3, not buff(s3)",
        "`s2",
        "`s4, x=5 or fsc",
        "`s1(all), cancel or s",
        "`fs, x=5"
      ],
      "coabs": [
        "Ieyasu",
        "Wand",
        "Forte"
      ],
      "share": [
        "Weapon",
        "Gala_Mym"
      ]
    }
    afflic_on_conf = {
        **afflic_conf,
        'sim_afflict': {'poison': 1}
    }
    _test_equip('Lathna', (afflic_conf, basic_conf, afflic_on_conf, basic_on_conf))

def test_equip_monoele():
    base_conf = {
      "slots.a": [
        "A_Man_Unchanging",
        "Memory_of_a_Friend",
        "Moonlight_Party",
        "From_Whence_He_Comes",
        "Bellathorna"
      ],
      "slots.d": "Epimetheus",
      "acl": [
        "`dragon(s), s=1",
        "`s3, not buff(s3)",
        "`s1",
        "`s2",
        "`s4, x=5"
      ],
      "coabs": [
        "Axe2",
        "Dagger2",
        "Tobias"
      ],
      "share": [
        "Weapon",
        "Formal_Joachim"
      ]
    }
    monoele_conf = {
      "slots.a": [
        "A_Man_Unchanging",
        "Memory_of_a_Friend",
        "Moonlight_Party",
        "From_Whence_He_Comes",
        "Bellathorna"
      ],
      "slots.d": "Epimetheus",
      "acl": [
        "`dragon(s), s=1",
        "`s3, not buff(s3)",
        "`s1",
        "`s2",
        "`s4, x=5"
      ],
      "coabs": [
        "Dagger",
        "Forte",
        "Cleo"
      ],
      "share": [
        "Weapon",
        "Gala_Mym"
      ]
    }
    _test_equip('Durant', (monoele_conf, base_conf))

def test_repair():
    basic_conf = {
        'slots.a': [
            'Candy_Couriers',
            'Me_and_My_Bestie',
            'Memory_of_a_Friend',
            'The_Plaguebringer',
            'To_the_Extreme'
        ],
        'slots.d': 'Gala_Mars',
        'acl': [
            '`dragon(s-s)',
            '`s3, not buff(s3) and x=5',
            '`s1',
            '`s4,cancel',
            '`s2, x=5'
        ],
        'coabs': [
            'Blade',
            'Joe',
            'Marth'
        ],
        'share': [
            'Weapon',
            'Durant'
        ]
    }
    equip_manager = _test_equip('Xania', (basic_conf,))
    equip_manager['180']['base']['dps'] = 222
    # print('~'*60)
    # pprint(equip_manager)
    # print('~'*60)
    # adv_module, _ = core.simulate.load_adv_module(equip_manager.advname)
    # element = load_adv_json(equip_manager.advname)['c']['ele']
    # equip_manager.repair_entry(adv_module, element, equip_manager['180']['base'], '180', 'base')
    # print('~'*60)
    # pprint(equip_manager)
    # print('~'*60)
    equip_manager.repair_entries()

if __name__ == '__main__':
    test_repair()