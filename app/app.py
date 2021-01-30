import io
import json
from conf import get_fullname
import os
import sys
import subprocess

from contextlib import redirect_stdout
from flask import Flask
from flask import request
from flask import jsonify

import core.simulate
from core.afflic import AFFLICT_LIST
from conf import (
    ROOT_DIR, TRIBE_TYPES, skillshare, wyrmprints, weapons, dragons, mono_elecoabs,
    load_adv_json, load_equip_json, list_advs
)
from conf.equip import initialize_equip_managers

app = Flask(__name__)

# Helpers
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
for fn in list_advs():
    core.simulate.load_adv_module(fn, in_place=ADV_MODULES)

EQUIP_MANAGERS = initialize_equip_managers()

def set_teamdps_res(result, logs, real_d, suffix=''):
    result['extra' + suffix] = {}
    if logs.team_buff > 0:
        result['extra' + suffix]['team_buff'] = '+{}%'.format(round(logs.team_buff / real_d * 100))
    for tension, count in logs.team_tension.items():
        if count > 0:
            result['extra' + suffix]['team_{}'.format(tension)] = '{} stacks'.format(round(count))
    return result

def run_adv_test(adv_name, wp=None, dra=None, wep=None, acl=None, conf=None, cond=None, vkey=None, t=180, log=5, mass=0):
    adv_module = ADV_MODULES[adv_name][vkey]

    if conf is None:
        conf = {}

    conf['flask_env'] = True
    if wp is not None:
        conf['slots.a'] = list(wp)
    if dra is not None:
        conf['slots.d'] = dra
    if wep is not None:
        conf['slots.w'] = wep
    if acl:
        conf['acl'] = acl

    result = {}

    fn = io.StringIO()
    try:
        run_res = core.simulate.test(adv_name, adv_module, conf, t, log, mass, output=fn, cond=cond)
        result['test_output'] = fn.getvalue()
    except Exception as e:
        result['error'] = str(e)
        # raise e
        return result

    adv = run_res[0][0]
    real_d = run_res[0][1]
    if vkey is None:
        # core.simulate.save_equip(adv, real_d)
        EQUIP_MANAGERS[adv_name].accept_new_entry(adv, real_d)

    result['logs'] = {}
    fn = io.StringIO()
    adv.logs.write_logs(output=fn, log_filter=[str(adv.slots.d.name), str(adv.slots.c.name)])
    result['logs']['dragon'] = fn.getvalue()
    fn = io.StringIO()
    core.simulate.act_sum(adv.logs.act_seq, fn)
    result['logs']['action'] = fn.getvalue()
    result['logs']['summation'] = '\n'.join(['{}: {}'.format(k, v) for k, v in adv.logs.counts.items() if v])
    fn = io.StringIO()
    adv.logs.write_logs(output=fn, maxlen=3000)
    result['logs']['timeline'] = fn.getvalue()

    result['chart'] = {}
    result['chart'] = adv.logs.convert_dataset()

    return result


# API
@app.route('/simc_adv_test', methods=['POST'])
def simc_adv_test():
    if not request.method == 'POST':
        return 'Wrong request method.'
    params = request.get_json(silent=True)
    adv_name = 'Patia' if not 'adv' in params or params['adv'] is None else params['adv']
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
    vkey = params.get('variant')
    # latency = 0 if 'latency' not in params else abs(float(params['latency']))
    # print(params, flush=True)

    conf = {}
    if 'missile' in params:
        missile = abs(float(params['missile']))
        if missile > 0:
            conf['missile_iv'] = missile
    if 'hp' in params:
        conf['hp'] = min(abs(int(params['hp'])), 100)
    if 'specialmode' in params:
        conf[params['specialmode']] = True
    if 'classbane' in params and (params['classbane'] in TRIBE_TYPES or params['classbane'] == 'HDT'):
        conf['classbane'] = params['classbane']
    if 'dumb' in params:
        conf['dumb'] = params['dumb']
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

    result = run_adv_test(
        adv_name,
        wp=wp, dra=dra, wep=wep, acl=acl,
        conf=conf, cond=cond, vkey=vkey, t=t, log=log, mass=mass
    )
    return jsonify(result)

@app.route('/simc_adv_slotlist', methods=['GET', 'POST'])
def get_adv_slotlist():
    result = {}
    result['adv'] = {}
    if request.method == 'GET':
        advname = request.args.get('adv', default=None)
        variant = request.args.get('variant', default=None)
        equip_key = request.args.get('equip', default=None)
        mono = bool(request.args.get('mono', default=None))
        duration = request.args.get('t', default=180)
    elif request.method == 'POST':
        params = request.get_json(silent=True)
        advname = params.get('adv', None)
        variant = params.get('variant', None)
        equip_key = params.get('equip', None)
        mono = bool(params.get('mono', None))
        duration = params.get('t', 180)
    else:
        return 'Wrong request method.'
    duration = max(min(((int(duration) // 60)*60), 180), 60)
    if advname is not None:
        adv = ADV_MODULES[advname][variant](name=advname, duration=duration, equip_key=equip_key)
        adv.config_slots()
        result['adv']['basename'] = adv.name
        result['adv']['ele'] = adv.slots.c.ele
        result['adv']['wt'] = adv.slots.c.wt
        result['adv']['pref_dra'] = adv.slots.d.qual
        result['adv']['pref_wep'] = adv.slots.w.qual
        result['adv']['pref_wp'] = adv.slots.a.qual_lst
        result['adv']['pref_coab'] = adv.conf['coabs'] or []
        result['adv']['pref_share'] = adv.conf['share'] or []
        result['adv']['acl'] = adv.conf.acl
        if adv.conf['tdps'] and 0 <= adv.conf['tdps'] <= 200000:
            result['adv']['tdps'] = int(adv.conf.tdps) + 1
        if adv.equip_key:
            result['adv']['equip'] = adv.equip_key

        available_wpn = {**weapons[adv.slots.c.wt]['any'], **weapons[adv.slots.c.wt][adv.slots.c.ele]}
        result['weapons'] = {}
        for series, wpn in sorted(available_wpn.items(), key=lambda w: -w[1]['w']['att']):
            result['weapons'][series] = f'{wpn["w"]["series"]} | {wpn["w"]["name"]}'
        result['dragons'] = {drg: data['d']['name'] for drg, data in dragons[adv.slots.c.ele].items()}
        # gold fafu lul
        result['dragons']['Gold_Fafnir'] = 'Gold Fafnir'
        if mono:
            result['coabilities'] = {k: (get_fullname(k), *v) for k, v in mono_elecoabs[adv.slots.c.ele].items()}
        else:
            result['coabilities'] = {k: (get_fullname(k), *v) for k, v in adv.slots.c.valid_coabs.items()}
    return jsonify(result)


@app.route('/simc_adv_wp_list', methods=['GET', 'POST'])
def get_adv_wp_list():
    if not (request.method == 'GET' or request.method == 'POST'):
        return 'Wrong request method.'
    result = {}
    result['adv'] = {}
    for name, variants in ADV_MODULES.items():
        result['adv'][name] = {
            'fullname': get_fullname(name),
            'variants': [vkey for vkey in variants.keys() if vkey is not None and vkey != 'mass']
        }
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
    return '<pre>' + json.dumps(load_equip_json(request.args.get('adv', default=None)), ensure_ascii=False, indent=4).replace('>', '&gt;').replace('<', '&lt;') + '</pre>'

@app.route('/simc_git_diff', methods=['GET'])
def get_git_diff():
    return '<pre>' + subprocess.check_output(['git', 'diff', 'conf/equip'], cwd=ROOT_DIR, encoding='UTF-8').replace('>', '&gt;').replace('<', '&lt;') + '</pre>'
