import io
import json
import inspect
from importlib.util import spec_from_file_location, module_from_spec
from conf import get_fullname
import os
import sys

from contextlib import redirect_stdout
from flask import Flask
from flask import request
from flask import jsonify

import core.simulate
from core.afflic import AFFLICT_LIST
from conf import ROOT_DIR, skillshare, wyrmprints, weapons, dragons, load_adv_json, load_equip_json, save_equip_json
app = Flask(__name__)

# Helpers
ADV_DIR = 'adv'
CHART_DIR = 'www/dl-sim'
DURATION_LIST = (60, 120, 180)

def load_chara_file(fn, extra=None):
    if extra:
        chara = list(extra)
    else:
        chara = []
    with open(os.path.join(ROOT_DIR, fn)) as f:
        for l in f:
            chara.append(l.strip().replace('.py', ''))
    return chara

NORMAL_ADV = load_chara_file('chara_quick.txt')
MASS_SIM_ADV = load_chara_file('chara_slow.txt')
PRELIM_ADV = load_chara_file('chara_prelim.txt')

SPECIAL_ADV = {
    'hunter_sarisse_allhits': {
        'fullname': 'Hunter Sarisse All Hits',
        'nc': []
    },
    'gala_alex_bk': {
        'fullname': 'Gala Alex Break Chain',
        'nc': []
    }
}

SIMULATED_BUFFS = {
    'str_buff': (-100, 200, 100),
    'def_down': (-50, 200, 100),
    'critr': (-100, 100, 100),
    'critd': (-100, 200, 100),
    'doublebuff_interval': (0.5, 600.0, 1),
    'count': (0, float('inf'), 1),
    'echo': (0, float('inf'), 1)
}


ADV_MODULES = {}
for adv in NORMAL_ADV+MASS_SIM_ADV+PRELIM_ADV:
    module = core.simulate.load_adv_module(adv)
    name = module.__name__
    ADV_MODULES[name] = module
for name, _ in SPECIAL_ADV.items():
    module = core.simulate.load_adv_module(name)
    ADV_MODULES[name] = module

def set_teamdps_res(result, logs, real_d, suffix=''):
    result['extra' + suffix] = {}
    if logs.team_buff > 0:
        result['extra' + suffix]['team_buff'] = '+{}%'.format(round(logs.team_buff / real_d * 100))
    for tension, count in logs.team_tension.items():
        if count > 0:
            result['extra' + suffix]['team_{}'.format(tension)] = '{} stacks'.format(round(count))
    return result

def run_adv_test(adv_name, wp=None, dra=None, wep=None, acl=None, conf=None, cond=None, t=180, log=5, mass=0):
    adv_module = ADV_MODULES[adv_name]

    if conf is None:
        conf = {}

    conf['flask_env'] = True
    if wp is not None:
        conf['slots.a'] = list(wp)
    if dra is not None:
        conf['slots.d'] = dra
    # if wep is not None:
    #     conf['slots.w'] = wep
    if acl:
        conf['acl'] = acl

    result = {}

    fn = io.StringIO()
    try:
        run_res, adv = core.simulate.test(adv_module, conf, t, log, mass, output=fn, cond=cond)
        result['test_output'] = fn.getvalue()
    except Exception as e:
        result['error'] = str(e)
        return result

    if not adv_name in SPECIAL_ADV:
        save_equip(adv, adv_module, result['test_output'])

    result['logs'] = {}
    adv = run_res[0][0]
    fn = io.StringIO()
    adv.logs.write_logs(output=fn, log_filter=[str(type(adv.slots.d).__name__), str(type(adv).__name__)])
    result['logs']['dragon'] = fn.getvalue()
    fn = io.StringIO()
    core.simulate.act_sum(adv.logs.act_seq, fn)
    result['logs']['action'] = fn.getvalue()
    result['logs']['summation'] = '\n'.join(['{}: {}'.format(k, v) for k, v in adv.logs.counts.items() if v])
    fn = io.StringIO()
    adv.logs.write_logs(output=fn)
    result['logs']['timeline'] = fn.getvalue()
    return result


BANNED_PRINTS = ('Witchs_Kitchen', 'Berry_Lovable_Friends', 'Happier_Times')
def save_equip(adv, adv_module, test_output):
    adv.duration = int(adv.duration)
    if adv.duration not in (60, 120, 180):
        return
    if 'sim_buffbot' in adv.conf:
        return
    if 'afflict_res' in adv.conf and 'afflict_res' not in adv.conf_base:
        return
    if 'dragonbattle' in adv.conf:
        return
    if 'hp' in adv.conf:
        return
    if any([wp in BANNED_PRINTS for wp in adv.slots.a.qual_lst]):
        return
    etype = 'base'
    eleaff = core.simulate.ELE_AFFLICT[adv.slots.c.ele]
    if adv.sim_afflict:
        if adv.sim_afflict != {eleaff} or \
           adv.conf_init.sim_afflict[eleaff] != 1:
            return
        else:
            etype = eleaff
    dkey = str(adv.duration)
    adv_qual = adv.__class__.__name__
    equip = load_equip_json(adv_qual)
    cached = None
    try:
        cached = equip[dkey][etype]
        cdps = cached.get('dps', 0)
        cteam = cached.get('team', 0)
    except KeyError:
        try:
            cached = equip[dkey]['base']
            cdps = cached.get('dps', 0)
            cteam = cached.get('team', 0)
        except KeyError:
            cdps = 0
            cteam = 0
    ndps = sum(map(lambda v: sum(v.values()), adv.logs.damage.values())) / adv.real_duration
    nteam = adv.logs.team_buff / adv.real_duration
    if ndps < cdps:
        if etype == 'base' and nteam > cteam:
            etype = 'buffer'
            try:
                cached = equip[dkey][etype]
                cdps = cached.get('dps', 0)
                cteam = cached.get('team', 0)
            except KeyError:
                pass
            if nteam < cteam:
                return
            if nteam == cteam:
                if cdps > ndps:
                    return
        else:
            return
    if etype == 'base' and nteam < cteam and 'buffer' not in equip[dkey]:
        equip[dkey]['buffer'] = cached
        equip[dkey]['buffer']['tdps'] = (ndps - cdps) / (cteam - nteam)
    if dkey not in equip:
        equip[dkey] = {}
    acl_list = adv.conf.acl
    if not isinstance(acl_list, list):
        acl_list = [line.strip() for line in acl_list.split('\n') if line.strip()]
    # do some san checks
    equip[dkey][etype] = {
        'dps': ndps,
        'team': nteam,
        'tdps': None,
        'slots.a': adv.slots.a.qual_lst,
        'slots.d': adv.slots.d.qual,
        'acl': acl_list,
        'coabs': adv.slots.c.coab_list,
        'share': adv.skillshare_list
    }
    if etype == 'base':
        try:
            cdps = equip[dkey][eleaff]['dps']
            if cdps < ndps:
                del equip[dkey][eleaff]
        except KeyError:
            pass
        try:
            cdps = equip[dkey]['buffer']['dps']
            cteam = equip[dkey]['buffer']['team']
            if cteam <= nteam:
                del equip[dkey]['buffer']
        except KeyError:
            pass
    try:
        dps_delta = equip[dkey]['base']['dps'] - equip[dkey]['buffer']['dps']
        team_delta = equip[dkey]['buffer']['team'] - equip[dkey]['base']['team']
        equip[dkey]['buffer']['tdps'] = dps_delta / team_delta
    except KeyError:
        pass
    # if 'buffer' in equip[dkey] and equip[dkey]['buffer']['team'] > 1.1:
    if 'buffer' in equip[dkey] and equip[dkey]['buffer']['tdps'] < 40000:
        equip[dkey]['pref'] = 'buffer'
        equip[dkey]['base']['tdps'] = equip[dkey]['buffer']['tdps']
    else:
        equip[dkey]['pref'] = 'base'
    save_equip_json(adv_qual, equip)

    # output = open(os.path.join(ROOT_DIR, CHART_DIR, 'chara', '{}.py.csv'.format(adv_qual.lower())), 'w', encoding='utf8')
    # for d in (60, 120, 180):
    #     core.simulate.test(adv_module, {}, duration=d, verbose=-5, output=output)
    # output.close()
    # core.simulate.combine()

# API
@app.route('/simc_adv_test', methods=['POST'])
def simc_adv_test():
    if not request.method == 'POST':
        return 'Wrong request method.'
    params = request.get_json(silent=True)
    adv_name = 'Euden' if not 'adv' in params or params['adv'] is None else params['adv']
    wp = params.get('wp')
    dra = params.get('dra')
    wep = params.get('wep')
    acl = params.get('acl')
    cond = params.get('condition') or None
    t = 180 if not 't' in params else min(abs(float(params['t'])), 600.0)
    log = 5
    mass = 0
    coab = params.get('coab')
    share = params.get('share')
    # latency = 0 if 'latency' not in params else abs(float(params['latency']))
    # print(params, flush=True)

    if adv_name in SPECIAL_ADV:
        not_customizable = SPECIAL_ADV[adv_name]['nc']
        if 'wp' in not_customizable:
            wp = None
        if 'acl' in not_customizable:
            acl = None
        if 'coab' in not_customizable:
            coab = None

    conf = {}
    if 'missile' in params:
        missile = abs(float(params['missile']))
        if missile > 0:
            conf['missile_iv'] = missile
    if 'hp' in params:
        conf['hp'] = min(abs(int(params['hp'])), 100)
    if 'dragonbattle' in params:
        conf['dragonbattle'] = bool(params['dragonbattle'])
    if coab is not None:
        conf['coabs'] = coab
    if share is not None:
        conf['share'] = share
    for afflic in AFFLICT_LIST:
        try:
            conf[f'sim_afflict.{afflic}'] = min(abs(int(params['sim_afflict'][afflic])), 100)/100
        except KeyError:
            pass
        try:
            conf[f'afflict_res.{afflic}'] = min(abs(int(params['afflict_res'][afflic])), 100)
        except KeyError:
            pass

    for buff, bounds in SIMULATED_BUFFS.items():
        b_min, b_max, b_ratio = bounds
        try:
            conf[f'sim_buffbot.{buff}'] = min(max(float(params['sim_buff'][buff]), b_min), b_max)/b_ratio
        except KeyError:
            pass

    result = run_adv_test(adv_name, wp, dra, wep, acl, conf, cond, t=t, log=log, mass=mass)
    return jsonify(result)

@app.route('/simc_adv_slotlist', methods=['GET', 'POST'])
def get_adv_slotlist():
    result = {}
    result['adv'] = {}
    if request.method == 'GET':
        advname = request.args.get('adv', default=None)
        equip_key = request.args.get('equip', default=None)
        duration = request.args.get('t', default=180)
    elif request.method == 'POST':
        params = request.get_json(silent=True)
        advname = params.get('adv')
        equip_key = params.get('equip')
        duration = params.get('t', 180)
    else:
        return 'Wrong request method.'
    duration = max(min(((int(duration) // 60)*60), 180), 60)
    if advname is not None:
        adv = ADV_MODULES[advname](duration=duration, equip_key=equip_key)
        adv.config_slots()
        result['adv']['basename'] = adv.__class__.__name__
        result['adv']['ele'] = adv.slots.c.ele
        result['adv']['wt'] = adv.slots.c.wt
        result['adv']['pref_dra'] = adv.slots.d.qual
        result['adv']['pref_wep'] = f'{adv.slots.c.ele}-{adv.slots.c.wt}'
        result['adv']['pref_wp'] = adv.slots.a.qual_lst
        try:
            result['adv']['pref_coab'] = adv.conf.coabs['base'] or []
        except:
            result['adv']['pref_coab'] = adv.conf['coabs'] or []
        try:
            result['adv']['pref_share'] = adv.conf.share['base'] or []
        except:
            result['adv']['pref_share'] = adv.conf['share'] or []
        result['adv']['acl'] = adv.conf.acl
        if 'afflict_res' in adv.conf:
            res_conf = adv.conf.afflict_res
            res_dict = {}
            for afflic in AFFLICT_LIST:
                if afflic in res_conf:
                    res_dict[afflic] = res_conf[afflic]
            if len(res_dict.keys()) > 0:
                result['adv']['afflict_res'] = res_dict
        if advname in SPECIAL_ADV:
            result['adv']['no_config'] = SPECIAL_ADV[advname]['nc']

        if adv.conf['tdps'] and 0 <= adv.conf['tdps'] <= 200000:
            result['adv']['tdps'] = int(adv.conf.tdps) + 1
        if adv.equip_key:
            result['adv']['equip'] = adv.equip_key

        weapon = weapons[adv.slots.c.ele][adv.slots.c.wt]
        weapon_name = f'Agito T{weapon["tier"]} {weapon["name"]}'
        result['weapons'] = {f'{adv.slots.c.ele}-{adv.slots.c.wt}': weapon_name}
        result['dragons'] = {drg: data['d']['name'] for drg, data in dragons[adv.slots.c.ele].items()}
        result['coabilities'] = {k: (get_fullname(k), *v) for k, v in adv.slots.c.valid_coabs.items()}
    return jsonify(result)


@app.route('/simc_adv_wp_list', methods=['GET', 'POST'])
def get_adv_wp_list():
    if not (request.method == 'GET' or request.method == 'POST'):
        return 'Wrong request method.'
    result = {}
    result['adv'] = {}
    for name in ADV_MODULES.keys():
        try:
            result['adv'][name] = load_adv_json(name)['c']['name']
        except FileNotFoundError:
            result['adv'][name] = SPECIAL_ADV[name]['fullname']
    wplists = {'gold':{}, 'silver':{}}
    for wp, data in wyrmprints.items():
        ab_str = f'-{data["union"]}'
        if data['a']:
            ab_str = '[' + '|'.join(map(str, data['a'][0])) + ']' + ab_str
        else:
            ab_str = '[]' + ab_str
        if data['rarity'] == 5:
            wplists['gold'][wp] = data['name'] + ' ' + ab_str
        else:
            wplists['silver'][wp] = data['name'] + ' ' + ab_str
    result['wyrmprints'] = wplists
    result['skillshare'] = {k: {'fullname': get_fullname(k), **v} for k, v in skillshare.items()}
    return jsonify(result)

@app.route('/simc_adv_equip', methods=['GET'])
def get_adv_equip():
    return '<pre>' + json.dumps(load_equip_json(request.args.get('adv', default=None)), ensure_ascii=False, indent=4) + '</pre>'