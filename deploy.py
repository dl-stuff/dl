import os
import sys
from copy import deepcopy
from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
from time import monotonic
import core.simulate
from conf import ROOT_DIR, load_equip_json, load_adv_json
from core.simulate import CHART_DIR, DURATION_LIST, QUICK_LIST_FILES, SLOW_LIST_FILES, ADV_LIST_FILES

ADV_DIR = 'adv'


def sim_adv(adv_file, special=None, mass=None, sanity_test=False):
    t_start = monotonic()

    adv_file = os.path.basename(adv_file)
    if adv_file.endswith('.py'):
        adv_name = adv_file.split('.')[0]
    else:
        adv_name = adv_file
        adv_file += '.py'
    adv_file = adv_file.lower()
    if special is None and adv_file.count('.py') > 1:
        special == True

    verbose = -5
    durations = DURATION_LIST
    if special:
        durations = [180]
    if sanity_test:
        mass = None
        durations = [30]
        output = open(os.devnull, 'w')
    else:
        output = open(os.path.join(ROOT_DIR, CHART_DIR, 'chara', '{}.csv'.format(adv_file)), 'w', encoding='utf8')

    try:
        adv_module = core.simulate.load_adv_module(adv_name)
    except Exception as e:
        print(f'\033[93m{monotonic()-t_start:.4f}s - sim:{adv_file} {e}\033[0m', flush=True)
        output.close()
        return
    try:
        for d in durations:
            core.simulate.test(adv_module, {}, duration=d, verbose=verbose, mass=1000 if mass else None, special=special, output=output)
        if not sanity_test:
            print('{:.4f}s - sim:{}'.format(monotonic() - t_start, adv_file), flush=True)
    except Exception as e:
        print(f'\033[91m{monotonic()-t_start:.4f}s - sim:{adv_file} {e}\033[0m', flush=True)
        output.close()
        return
    output.close()


def run_and_save(adv_module, ele, dkey, ekey, conf):
    if ekey == 'affliction':
        aff_name = core.simulate.ELE_AFFLICT[ele]
        conf[f'sim_afflict.{aff_name}'] = 1
    with open(os.devnull, 'w') as output:
        run_res = core.simulate.test(adv_module, conf, duration=int(dkey), verbose=0, output=output)
        core.simulate.save_equip(run_res[0][0], run_res[0][1], repair=True)


EQUIP_KEYS = ['base', 'buffer', 'affliction']
def repair_equips(adv_file):
    t_start = monotonic()
    # try:
    adv_file = os.path.basename(adv_file)
    adv_name = adv_file
    if adv_file.endswith('.py'):
        adv_name = adv_file.split('.')[0]
    adv_module = core.simulate.load_adv_module(adv_name)
    adv_name = adv_module.__name__
    adv_ele = load_adv_json(adv_name)['c']['ele']
    adv_equip = deepcopy(load_equip_json(adv_name))

    eleaff = None
    for dkey, equip_d in adv_equip.items():
        for ekey, conf in equip_d.items():
            if ekey == 'pref':
                continue
            run_and_save(adv_module, adv_ele, dkey, ekey, conf)
            # check if 180 equip is actually better for 120/60
            if dkey == '180':
                continue
            try:
                run_and_save(adv_module, adv_ele, dkey, ekey, equip_d['180'][ekey])
            except KeyError:
                pass
    # except Exception as e:
    #     print(f'\033[91m{monotonic()-t_start:.4f}s - repair:{adv_file} {e}\033[0m', flush=True)
    #     return
    print('{:.4f}s - repair:{}'.format(monotonic() - t_start, adv_file), flush=True)


def sim_adv_list(list_file, sanity_test=False, repair=False):
    special = list_file.startswith('chara_sp')
    mass = list_file.endswith('slow.txt') and not special
    with open(os.path.join(ROOT_DIR, list_file), encoding='utf8') as f:
        sorted_f = list(sorted(f))
    for adv_file in sorted_f:
        if repair:
            repair_equips(adv_file.strip())
        else:
            sim_adv(adv_file.strip(), special, mass, sanity_test, repair)
    with open(os.path.join(ROOT_DIR, list_file), 'w', encoding='utf8') as f:
        for adv_file in sorted_f:
            f.write(adv_file.strip())
            f.write('\n')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('USAGE python {} sim_targets [-c] [-sp]'.format(sys.argv[0]))
        exit(1)
    t_start = monotonic()

    arguments = sys.argv.copy()[1:]
    do_combine = False
    is_special = None
    is_mass = None
    sanity_test = False
    if '-c' in arguments:
        do_combine = True
        arguments.remove('-c')
    if '-sp' in arguments:
        is_special = True
        arguments.remove('-sp')
    if '-m' in arguments:
        is_mass = True
        arguments.remove('-m')
    if '-san' in arguments:
        sanity_test = True
    if '-rp' in arguments:
        arguments.remove('-rp')
        is_repair = True

    sim_targets = arguments

    if sanity_test or 'all' in sim_targets:
        list_files = ADV_LIST_FILES
    elif 'quick' in sim_targets:
        list_files = QUICK_LIST_FILES
    elif 'slow' in sim_targets:
        list_files = SLOW_LIST_FILES
    else:
        list_files = None
        sim_targets = [a for a in sim_targets if not a.startswith('-')]

    if list_files is not None:
        do_combine = True
        for list_file in list_files:
            sim_adv_list(list_file, sanity_test=sanity_test, repair=is_repair)
    else:
        for adv_file in sim_targets:
            if is_repair:
                repair_equips(adv_file)
            else:
                sim_adv(adv_file, special=is_special, mass=is_mass, sanity_test=sanity_test)

    if do_combine and not sanity_test:
        core.simulate.combine()

    print('total: {:.4f}s'.format(monotonic() - t_start))
