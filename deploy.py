import os
import sys
from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
from time import monotonic
import core.simulate

ROOT_DIR = '.'
ADV_DIR = 'adv'
OUTPUT_DIR = 'www/dl-sim'
SIMC_EX_LIST = ['_', 'd', 'b', 'db']
REAL_EX_LIST = ['_', 'k', 'r', 'kr', 'b', 'kb', 'rb', 'krb', 'd', 'kd', 'rd', 'krd', 'db', 'kdb', 'rdb', 'krdb']
DURATION_LIST = [60, 120, 180]
QUICK_LIST_FILES = ['chara_quick.txt', 'chara_sp_quick.txt']
SLOW_LIST_FILES = ['chara_slow.txt', 'chara_sp_slow.txt']
ADV_LIST_FILES = QUICK_LIST_FILES + SLOW_LIST_FILES

def load_adv_module_special(adv_file):
    adv_name = adv_file.split('.')[0]
    fn = os.path.join(ROOT_DIR, ADV_DIR, adv_file)
    spec = spec_from_file_location(adv_name, fn)
    module = module_from_spec(spec)
    sys.modules[adv_name] = module
    spec.loader.exec_module(module)
    return module.module()

def load_adv_module_normal(adv_file):
    adv_name = adv_file.split('.')[0]
    return getattr(
        __import__('adv.{}'.format(adv_name.lower())),
        adv_name.lower()
    ).module()

def sim_adv(adv_file, special=None, mass=None):
    t_start = monotonic()

    adv_file = os.path.basename(adv_file)
    output = open(os.path.join(ROOT_DIR, OUTPUT_DIR, 'chara', '{}.csv'.format(adv_file)), 'w')
    if special is None and adv_file.count('.py') > 1:
        special == True
    if special:
        durations = [180]
        load_adv_module = load_adv_module_special
    else:
        durations = DURATION_LIST
        load_adv_module = load_adv_module_normal
    adv_module = load_adv_module(adv_file)
    for d in durations:
        for ex in SIMC_EX_LIST:
            core.simulate.test(adv_module, {}, ex=ex, duration=d, verbose=-5, mass=1000 if mass else None, special=special, output=output)
    print('{:.4f}s - sim:{}'.format(monotonic() - t_start, adv_file), flush=True)

def sim_adv_list(list_file):
    special = list_file.startswith('chara_sp')
    mass = list_file.endswith('slow.txt') and not special
    with open(os.path.join(ROOT_DIR, list_file)) as f:
        for adv_file in f:
            sim_adv(adv_file.strip(), special, mass)

def combine():
    dst_dict = {}
    pages = [str(d) for d in DURATION_LIST] + ['sp']
    for p in pages:
        dst_dict[p] = {}
        for ex in REAL_EX_LIST:
            dst_dict[p][ex] = open(os.path.join(ROOT_DIR, OUTPUT_DIR, p, 'data_{}.csv'.format(ex)), 'w')

    for list_file in ADV_LIST_FILES:
        with open(os.path.join(ROOT_DIR, list_file)) as src:
            c_page, c_ex = '60', '_'
            for adv_file in src:
                adv_file = adv_file.strip()
                with open(os.path.join(ROOT_DIR, OUTPUT_DIR, 'chara', '{}.csv'.format(adv_file)), 'r') as chara:
                    for line in chara:
                        if line[0] == '-':
                            _, c_page, c_ex = line.strip().split(',')
                        else:
                            dst_dict[c_page][c_ex].write(line.strip())
                            dst_dict[c_page][c_ex].write('\n')
            print('cmb:{}'.format(list_file), flush=True)

    for p in pages:
        for ex in REAL_EX_LIST:
            dst_dict[p][ex].close()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('USAGE python {} sim_targets [-c] [-sp]'.format(sys.argv[0]))
        exit(1)
    t_start = monotonic()

    arguments = sys.argv.copy()[1:]
    do_combine = False
    is_special = None
    is_mass = None
    if '-c' in arguments:
        do_combine = True
        arguments.remove('-c')
    if '-sp' in arguments:
        is_special = True
        arguments.remove('-sp')
    if '-m' in arguments:
        is_mass = True
        arguments.remove('-m')

    sim_targets = arguments

    if 'all' in sim_targets:
        list_files = ADV_LIST_FILES
    elif 'quick' in sim_targets:
        list_files = QUICK_LIST_FILES
    elif 'slow' in sim_targets:
        list_files = SLOW_LIST_FILES
    else:
        list_files = None
        sim_targets = [a for a in sim_targets if a.endswith('.py')]

    if list_files is not None:
        do_combine = True
        for list_file in list_files:
            sim_adv_list(list_file)
    else:
        for adv_file in sim_targets:
            sim_adv(adv_file, special=is_special, mass=is_mass)

    if do_combine:
        combine()

    print('total: {:.4f}s'.format(monotonic() - t_start))
