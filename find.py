import os
import json
from core.simulate import load_adv_module
from deploy import ROOT_DIR
import random
from conf import load_adv_json

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
    stat_conf(lambda d: d['c']['ele'] == 'shadow')
