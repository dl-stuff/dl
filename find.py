import os
import json
from core.simulate import load_adv_module
from deploy import ROOT_DIR
import random
from conf import load_adv_json

ADV_LISTS = ['chara_quick.txt', 'chara_slow.txt']

def stat_shared():
    has_shared = {}
    no_shared = []
    for list_file in ADV_LISTS:
        with open(os.path.join(ROOT_DIR, list_file)) as f:
            for adv_file in f:
                adv_file = os.path.basename(adv_file).strip().split('.')[0]
                adv_module = load_adv_module(adv_file)
                if adv_module.conf['share']:
                    has_shared[adv_file] = adv_module.conf['share']
                else:
                    no_shared.append(adv_file)

    print('Has Shared', len(has_shared))
    for item in has_shared.items():
        print(*item)
    print('\nNo Shared', len(no_shared))
    for idx, adv in enumerate(no_shared):
        print(adv, end='\t' if (idx+1) % 5 else '\n')
    

    random.seed(5)
    print('\n\nDo:')
    print('\n'.join(random.sample(no_shared, 10)))

def stat_conf(cond):
    deploy = './python deploy.py '
    for root, dirs, files in os.walk('./conf/adv'):
        for fn in files:
            name, ext = os.path.splitext(fn)
            if ext != '.json':
                continue
            with open(os.path.join(root, fn)) as f:
                data = json.load(f)
                if cond(data):
                    deploy += name + ' '
    print(deploy)

def get_all_adv():
    adv_dict = {}
    for list_file in ADV_LISTS:
        with open(os.path.join(ROOT_DIR, list_file)) as f:
            for adv_file in f:
                adv_file = os.path.basename(adv_file).strip().split('.')[0]
                adv_module = load_adv_module(adv_file)
                adv_dict[adv_module.__name__] = adv_module
    return adv_dict


def move_abl():
    with open(ADV_CONF) as f:
        data = json.load(f)
    for list_file in ADV_LISTS:
        with open(os.path.join(ROOT_DIR, list_file)) as f:
            for adv_file in f:
                adv_file = os.path.basename(adv_file).strip().split('.')[0]
                adv_module = load_adv_module(adv_file)
                adv_name = str(adv_module.__name__)
                abl = []
                for ab in (adv_module.a1, adv_module.a2, adv_module.a3):
                    if ab:
                        if isinstance(ab, list):
                            abl.extend(ab)
                        else:
                            abl.append(ab)
                data[adv_name]['c']['a'] = abl
    with open(ADV_CONF, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)

def get_acl():
    adv_dict = get_all_adv()
    acl_map = {}
    for adv, module in adv_dict.items():
        acl_map[adv] = module.conf['acl']
    return acl_map

if __name__ == '__main__':
    stat_conf(lambda d: d['c']['ele'] == 'light')