from collections import deque
from pprint import pprint
from conf import load_json, save_json, DURATION

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

    def better_than(self, other):
        return self.weighted > other.weighted

    def update_threshold(self, other):
        if self['team'] != other['team']:
            self['tdps'] = (self['dps'] - other['dps']) / (other['team'] - self['team'])
            other['tdps'] = -self['tdps']
        else:
            self['team'] = None
            other['tdps'] = None

def build_entry_from_sim(entryclass, adv, real_d):
    entryclass.eligablility(adv)
    ndps = sum(map(lambda v: sum(v.values()), adv.logs.damage.values())) / real_d
    nteam = adv.logs.team_buff / real_d
    new_equip = {
        'dps': ndps,
        'team': nteam,
        'tdps': None,
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

EQUIP_ENTRY_MAP = {
    'base': EquipEntry,
    # 'buffer': BufferEntry,
    # 'affliction': AfflictionEntry,
    # 'affbuff' ?
    # 'mono_base': MonoEleEntry,
    # 'mono_buffer': MonoEleBufferEntry,
    # 'mono_affliction': MonoAfflictionEntry
}
KICK_TO = {
    'base': ('buffer', 'mono_base'),
    'buffer': ('base', 'mono_buffer'),
    'affliction': ('buffer', 'mono_affliction')
}


class EquipManager(dict):
    def __init__(self, advname, debug=False):
        if debug:
            super().__init__({})
            self.advname = 'Xania'
            self.debug = True
        else:
            super().__init__(load_json(f'equip/{advname}.json'))
            self.advname = advname
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
        kicked_entries = deque()
        need_write = False
        if duration not in self:
            self[duration] = {}
        for kind, entryclass in EQUIP_ENTRY_MAP.items():
            try:
                new_entry = build_entry_from_sim(entryclass, adv, real_d)
            except ValueError:
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
        # do kicked entry handling here
        if self.debug:
            print('~'*60)
            pprint(self)
            print('~'*60)
        elif need_write:
            save_json(f'equip/{adv}.json', self, indent=2)


def test_equip_simple():
    import core.simulate
    adv_name = 'Xania'
    adv_module, adv_name = core.simulate.load_adv_module(adv_name)
    equip_manager = EquipManager(adv_name, debug=True)

    lower_dps_conf = {
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
            'Kleimann'
        ]
    }
    run_res = core.simulate.test(adv_name, adv_module, lower_dps_conf, 180)
    adv = run_res[0][0]
    real_d = run_res[0][1]
    equip_manager.accept_new_entry(adv, real_d)

    higher_dps_conf = {
        **lower_dps_conf,
        'share': [
            'Weapon',
            'Formal_Joachim'
        ]
    }
    run_res = core.simulate.test(adv_name, adv_module, higher_dps_conf, 180)
    adv = run_res[0][0]
    real_d = run_res[0][1]
    equip_manager.accept_new_entry(adv, real_d)

if __name__ == '__main__':
    test_equip_simple()