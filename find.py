import os
import json
from deploy import ROOT_DIR
import random
from conf import load_adv_json, skillshare
import core.simulate

from pprint import pprint

ADV_LISTS = ['chara_quick.txt', 'chara_slow.txt']

def stat_conf(cond):
    deploy = 'python deploy.py '
    for root, dirs, files in os.walk('./conf/adv'):
        for fn in files:
            name, ext = os.path.splitext(fn)
            if ext != '.json':
                continue
            with open(os.path.join(root, fn)) as f:
                data = json.load(f)
                if cond(data):
                    deploy += name + ' '
    deploy += '-rp'
    print(deploy)

SPPS = 500
def rank_ss():
    ranked = []
    for adv, ss in skillshare.items():
        if ss.get('type') != 1:
            continue
        adv_data = load_adv_json(adv)
        try:
            skill = adv_data[f's{ss["s"]}']
        except:
            skill = adv_data[f's{ss["s"]}_phase1']
        try:
            mod_t = 0
            for attr in skill['attr']:
                dmg = attr.get('dmg', 0)
                killer = attr.get('killer')
                if killer:
                    dmg *= killer[0]
                mod_t += dmg
        except:
            continue
        ss_sp = ss['sp']
        normalized_t = skill['startup'] + skill['recovery'] + ss_sp / SPPS
        ranked.append((
            mod_t / normalized_t,
            adv_data['c']['name']
        ))
    pprint(sorted(ranked, reverse=True))

if __name__ == '__main__':
    # stat_conf(lambda d: d['c']['ele'] == 'water')
    rank_ss()
