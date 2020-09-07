import os
import sys
from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
from time import monotonic
import core.simulate

ROOT_DIR = '.'
ADV_DIR = 'adv'
OUTPUT_DIR = 'www/dl-sim'
DURATION_LIST = [60, 120, 180]
QUICK_LIST_FILES = ['chara_quick.txt', 'chara_sp_quick.txt']
SLOW_LIST_FILES = ['chara_slow.txt', 'chara_sp_slow.txt']
ADV_LIST_FILES = QUICK_LIST_FILES + SLOW_LIST_FILES


def sim_adv(adv_file, special=None, mass=None):
    t_start = monotonic()

    adv_file = os.path.basename(adv_file)
    if adv_file.endswith('.py'):
        adv_name = adv_file.split('.')[0]
    else:
        adv_name = adv_file
        adv_file += '.py'
    output = open(os.path.join(ROOT_DIR, OUTPUT_DIR,
                               'chara', '{}.csv'.format(adv_file)), 'w', encoding='utf8')
    if special is None and adv_file.count('.py') > 1:
        special == True
    if special:
        durations = [180]
    else:
        durations = DURATION_LIST
    try:
        adv_module = core.simulate.load_adv_module(adv_name)
    except Exception:
        print('\033[93m{:.4f}s - sim:{} NOT FOUND\033[0m'.format(monotonic() - t_start, adv_file), flush=True)
        return
    try:
        for d in durations:
            core.simulate.test(adv_module, {}, duration=d, verbose=-5,
                            mass=1000 if mass else None, special=special, output=output)
        print('{:.4f}s - sim:{}'.format(monotonic() - t_start, adv_file), flush=True)
    except Exception:
        print('\033[91m{:.4f}s - sim:{} FAILED\033[0m'.format(monotonic() - t_start, adv_file), flush=True)
        return


def sim_adv_list(list_file):
    special = list_file.startswith('chara_sp')
    mass = list_file.endswith('slow.txt') and not special
    with open(os.path.join(ROOT_DIR, list_file), encoding='utf8') as f:
        sorted_f = sorted(f)
    with open(os.path.join(ROOT_DIR, list_file), 'w', encoding='utf8') as f:
        for adv_file in sorted_f:
            sim_adv(adv_file.strip(), special, mass)
            f.write(adv_file)


def download_writeups():
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials

    KEYFILE = './adv-haste-d888baf004e9.json'
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(KEYFILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open('dl-adv-writeups').sheet1

    with open(os.path.join(ROOT_DIR, OUTPUT_DIR, 'chara', '_writeups.csv'), 'w', encoding='utf8') as f:
        for line in sheet.get_all_values()[1:]:
            f.write(line[0])
            f.write(',')
            f.write('"')
            f.write(line[1])
            f.write('"')
            f.write('\n')


def combine():
    dst_dict = {}
    pages = [str(d) for d in DURATION_LIST] + ['sp']
    aff = ['_', 'affliction']
    for p in pages:
        dst_dict[p] = {}
        for a in aff:
            dst_dict[p][a] = open(os.path.join(
                ROOT_DIR, OUTPUT_DIR, 'page/{}_{}.csv'.format(p, a)), 'w')

    for list_file in ADV_LIST_FILES:
        with open(os.path.join(ROOT_DIR, list_file), encoding='utf8') as src:
            c_page, c_aff = '60', '_'
            for adv_file in src:
                adv_file = adv_file.strip()
                src = os.path.join(ROOT_DIR, OUTPUT_DIR,
                                   'chara', '{}.csv'.format(adv_file))
                if not os.path.exists(src):
                    continue
                with open(src, 'r', encoding='utf8') as chara:
                    for line in chara:
                        if line[0] == '-':
                            _, c_page, c_aff = line.strip().split(',')
                        else:
                            dst_dict[c_page][c_aff].write(line.strip())
                            dst_dict[c_page][c_aff].write('\n')
            print('cmb:{}'.format(list_file), flush=True)

    for p in pages:
        for a in aff:
            dst_dict[p][a].close()
            dst_dict[p][a].close()


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
    if '-dw' in arguments:
        download_writeups()

    sim_targets = arguments

    if 'all' in sim_targets:
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
            sim_adv_list(list_file)
    else:
        for adv_file in sim_targets:
            sim_adv(adv_file, special=is_special, mass=is_mass)

    if do_combine:
        combine()

    print('total: {:.4f}s'.format(monotonic() - t_start))
