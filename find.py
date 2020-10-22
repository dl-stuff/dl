import os
import json
from deploy import ROOT_DIR
import random
from conf import load_adv_json
import core.simulate

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
    print(deploy)

if __name__ == '__main__':
    # stat_conf(lambda d: d['c']['ele'] == 'shadow')

    ADV_MODULES = {}
    for root, dirs, files in os.walk(os.path.join(ROOT_DIR, 'conf', 'adv')):
        for fn in files:
            name, ext = os.path.splitext(fn)
            if ext != '.json':
                continue
            core.simulate.load_adv_module(name, in_place=ADV_MODULES)

    from pprint import pprint
    pprint(ADV_MODULES)
