import sys
import os
import re
import time
import json
from itertools import chain
from collections import defaultdict
from conf import ROOT_DIR, get_icon, get_fullname, load_equip_json, save_equip_json
import core.acl
import core.advbase

BR = 64
def skill_efficiency(real_d, team_dps, mod):
    return (team_dps * 1.25) * mod * 2 / 5 / real_d
tension_efficiency = {
    'energy': 0.5,
    'inspiration': 0.6
}

ELE_AFFLICT = {
    'flame': 'burn',
    'water': 'frostbite',
    'wind': 'poison',
    'light': 'paralysis',
    'shadow': 'poison'
}

DOT_AFFLICT = ['poison', 'paralysis', 'burn', 'frostbite']

S_ALT = '†'

def run_once(name, module, conf, duration, cond, equip_key=None):
    adv = module(name=name, conf=conf, duration=duration, cond=cond, equip_key=equip_key)
    real_d = adv.run()
    return adv, real_d

# Using starmap
import multiprocessing
def run_once_mass(name, module, conf, duration, cond, equip_key, idx):
    adv = module(name=name, conf=conf, duration=duration, cond=cond)
    real_d = adv.run()
    return adv.logs, real_d

def sum_logs(log, other):
    for k1 in log.damage:
        for k2 in log.damage[k1]:
            try:
                log.damage[k1][k2] += other.damage[k1][k2]
            except:
                continue
    log.team_buff += other.team_buff
    for k in log.team_tension:
        try:
            log.team_tension[k] += other.team_tension[k]
        except:
            continue
    return log

def avg_logs(log, mass):
    for k1 in log.damage:
        for k2 in log.damage[k1]:
            log.damage[k1][k2] /= mass
    log.team_buff /= mass
    for k in log.team_tension:
        log.team_tension[k] /= mass
    return log

def run_mass(mass, base_log, base_d, name, module, conf, duration, cond, equip_key=None):
    mass = 1000 if mass == 1 else mass
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        for log, real_d in pool.starmap(run_once_mass, [(name, module, conf, duration, cond, equip_key, idx) for idx in range(mass-1)]):
            base_log = sum_logs(base_log, log)
            base_d += real_d
    base_log = avg_logs(base_log, mass)
    base_d /= mass
    return base_log, base_d

def test(name, module, conf={}, duration=180, verbose=0, mass=None, output=None, cond=True, special=False):
    output = output or sys.stdout
    if verbose == 2:
        # output.write(adv._acl_str)
        adv = module(name=name)
        output.write(str(core.acl.build_acl(adv.conf.acl)._acl_str))
        output.write(str(core.acl.build_acl(adv.conf.acl)._tree.pretty()))
        return
    run_results = []
    adv, real_d = run_once(name, module, conf, duration, cond, equip_key=None)
    if verbose == 255:
        output.write(str(adv.slots))
        output.write('\n')
        act_sum(adv.logs.act_seq, output)
        output.write('\n\n')
        return
    if verbose == 1:
        adv.logs.write_logs(output=output)
        act_sum(adv.logs.act_seq, output)
        return

    if mass:
        adv.logs, real_d = run_mass(mass, adv.logs, real_d, name, module, conf, duration, cond)
    run_results.append((adv, real_d, True))

    aff_name = ELE_AFFLICT[adv.slots.c.ele]

    if -10 <= verbose <= -5:
        aff_name = ELE_AFFLICT[adv.slots.c.ele]
        conf[f'sim_afflict.{aff_name}'] = 1
        if verbose < -5:
            for aff_name in DOT_AFFLICT[:(-verbose-6)]:
                conf[f'sim_afflict.{aff_name}'] = 1
        equip_key = 'affliction' if adv.equip_key != 'buffer' else 'buffer'
        adv, real_d = run_once(name, module, conf, duration, cond, equip_key=equip_key)
        if mass:
            adv.logs, real_d = run_mass(mass, adv.logs, real_d, name, module, conf, duration, cond, equip_key=equip_key)
        run_results.append((adv, real_d, 'affliction'))

    for a, d, c in run_results:
        if verbose == -2:
            report(d, a, output, cond=c, web=False)
        elif abs(verbose) == 5:
            page = 'sp' if special else int(duration)
            if c:
                output.write('-,{},{}\n'.format(page, c if isinstance(c, str) else '_'))
            report(d, a, output, cond=c, web=True)
        else:
            if c == 'affliction':
                output.write('-'*BR+'\n')
                output.write(' & '.join(adv.sim_afflict))
                output.write('\n')
            summation(d, a, output, cond=c)

    return run_results

def slots(adv):
    slots = f'[{adv.slots.d}][{adv.slots.w}][{adv.slots.a}]\n'
    slots += '-'*(len(adv.name)) + ' '
    slots += f'[{"|".join((map(get_fullname, adv.slots.c.coab_list)))}][S3:{get_fullname(adv.skillshare_list[0])}'
    try:
        slots += f'|S4:{get_fullname(adv.skillshare_list[1])}]'
    except:
        slots += ']'
    return slots

def slots_csv(adv, web):
    padded_coab = adv.slots.c.coab_list.copy()
    if len(padded_coab) < 3:
        padded_coab.extend(['']*(3-len(padded_coab)))
    padded_share = adv.skillshare_list.copy()
    if len(padded_share) < 2:
        padded_share.extend(['']*(2-len(padded_share)))
    if not web:
        return (str(adv.slots), *padded_coab, *padded_share)
    icon_lst = []
    for name in chain(padded_coab, padded_share):
        if not name:
            icon_lst.extend(('', ''))
        else:
            icon_lst.extend((get_fullname(name), get_icon(name)))
    return (
        adv.slots.full_slot_icons(),
        *icon_lst
    )

def append_condensed(condensed, act):
    if len(condensed) > 0:
        l_act, l_cnt = condensed[-1]
        if l_act == act:
            condensed[-1] = (l_act, l_cnt+1)
            return condensed
    condensed.append((act, 1))
    return condensed

def act_repeats(condensed):
    from collections import Counter
    condensed = list(filter(lambda a: a[0] != 'dshift', condensed))
    start = 0
    maxlen = len(condensed)
    bestest = condensed, 1, 0
    for start in range(0, maxlen):
        accumulator = Counter()
        length = 1
        c_slice = tuple(condensed[start:start+length])
        while start+length*(accumulator[c_slice]+1) <= maxlen:
            n_slice = tuple(condensed[start+length*accumulator[c_slice]:start+length*(accumulator[c_slice]+1)])
            if n_slice == c_slice:
                accumulator[c_slice] += 1
            else:
                length += 1
                c_slice = tuple(condensed[start:start+length])
                accumulator[c_slice] = 1
        c_best = accumulator.most_common(1)
        if len(c_best) > 0 and c_best[0][1] > bestest[1]:
            bestest = (*c_best[0], start)
    return bestest

def act_sum(actions, output):
    p_act = '_'
    p_xseq = 0
    condensed = []
    for act in actions:
        act1 = act.split('_')[0]
        if act[0] == 'x':
            xseq = int(act1[1:])
            if xseq < p_xseq:
                condensed = append_condensed(condensed, p_act)
            p_xseq = xseq
        elif (act.startswith('fs') or act == 'd') and p_act[0] == 'x':
            p_xseq = 0
            condensed = append_condensed(condensed, p_act+act1)
        else:
            if p_act[0] == 'x':
                condensed = append_condensed(condensed, p_act)
            p_xseq = 0
            condensed = append_condensed(condensed, act)
        p_act = act1
    if p_act[0] == 'x':
        condensed = append_condensed(condensed, p_act)
    seq, freq, start = act_repeats(condensed)
    seqlen = len(seq)
    if freq < 2 or freq*seqlen < len(condensed) // 4:
        seqlen = 24
        freq = len(condensed) // seqlen
        start = 0
    p_type = None
    idx_offset = 0
    for idx, ac in enumerate(condensed):
        act, cnt = ac
        idx = idx - idx_offset
        if start > idx > 0 and idx % 24 == 0:
            output.write('\n')
        elif freq >= 0 and start < idx and (idx-start) % seqlen == 0:
            output.write('\n')
            freq -= 1
        elif idx > 0:
            output.write(' ')
        if act[0] == 'x' or act.startswith('fs'):
            if act[0] == 'x':
                act = 'c' + act[1:]
            if act[:2] == 'fs':
                parts = act.split('_')
                if len(parts) > 1:
                    act = act.split('_')[0] + '-' + parts[1][0]
            output.write(act)
            p_type = 'x'
        else:
            if act == 'dshift':
                output.write('[--- dragon ---]')
                p_type == 'd'
                idx_offset += 1
            else:
                parts = act.split('_')
                if len(parts) > 1:
                    if parts[1][:5] == 'phase':
                        act = parts[0]+'-'+parts[1][-1]
                    else:
                        act = parts[0]+'-'+parts[1][0]
                output.write('['+act+']')
                p_type = 's'
        if cnt > 1:
            output.write('*{}'.format(cnt))

def dps_sum(real_d, damage):
    res = {'dps':0}
    for k, v in damage.items():
        ds = dict_sum(v)
        res[k] = ds / real_d
        res['dps'] += ds
    res['dps'] = res['dps'] / real_d
    return res

def dict_sum(sub):
    return sum(sub.values())

def condense_damage_counts(dmg, cnt, rule):
    found_keys = set()
    cdmg, ccnt = defaultdict(lambda: 0), defaultdict(lambda: 0)
    for k in dmg.keys():
        found_keys.add(k)
        adj_k = rule(k)
        cdmg[adj_k] += dmg[k]
        if k in cnt:
            ccnt[adj_k] += cnt[k]
    for k in filter(lambda k: k not in found_keys, cnt.keys()):
        adj_k = rule(k)
        ccnt[adj_k] += cnt[k]
        if k in dmg:
            cdmg[adj_k] += dmg[k]
    return dict(cdmg), dict(ccnt)

def x_rule(k):
    ck = k.split('_')
    return 'x' if len(ck) == 1 else f'x_{ck[1]}'

def d_rule(k):
    return 'dx' if k.startswith('dx') else k

def damage_counts(real_d, damage, counts, output, res=None):
    if res is None:
        res = dps_sum(real_d, damage)
    found_dmg = set()
    for k1 in damage.keys():
        dmg = damage.get(k1)
        cnt = counts.get(k1)
        if dmg or cnt:
            output.write('\n{:>1} {:>3.0f}%| '.format(k1, res[k1] * 100 / res['dps']))
        if k1 == 'x':
            dmg, cnt = condense_damage_counts(dmg, cnt, x_rule)
        if k1 == 'd':
            dmg, cnt = condense_damage_counts(dmg, cnt, d_rule)
        for k2, v2 in sorted(cnt.items(), key=lambda item: item[0]):
            if dmg.get(k2):
                output.write('{}: {:d} [{}], '.format(k2, int(dmg[k2]), v2))
                found_dmg.add(k2)
            else:
                output.write('{}: [{}], '.format(k2, v2))
        for k2, v2 in sorted(dmg.items(), key=lambda item: item[0]):
            if k2 not in found_dmg:
                output.write('{}: {:d}, '.format(k2, int(v2)))

    # found_dmg = set()
    # for k1, v1 in (counts.items()):
    #     d1 = damage[k1]
    #     if v1 or damage.get(k1):
    #         output.write('\n{:>1} {:>3.0f}%| '.format(k1, res[k1] * 100 / res['dps']))
    #     if k1 == 'x':
    #         ccnt, cdmg = defaultdict(lambda: 0), defaultdict(lambda: 0)
    #         for k2, v2 in v1.items():
    #             ck = k2.split('_')
    #             ck = 'x' if len(ck) == 1 else f'x_{ck[1]}'
    #             ccnt[ck] += v2
    #             if d1.get(k2):
    #                 cdmg[ck] += d1.get(k2)
    #         v1 = dict(ccnt)
    #         d1 = dict(cdmg)
    #     elif k1 == 'd':
    #         ccnt, cdmg = defaultdict(lambda: 0), defaultdict(lambda: 0)
    #         for k2, v2 in d1.items():
    #             dk = 'dx' if k2.startswith('dx') else k2
    #             if v1.get(dk):
    #                 ccnt[dk] += v1.get(dk)
    #             cdmg[dk] += v2
    #         v1 = dict(ccnt)
    #         d1 = dict(cdmg)
    #     for k2, v2 in sorted(v1.items(), key=lambda item: item[0]):
    #         if d1.get(k2):
    #             output.write('{}: {:d} [{}], '.format(k2, int(d1[k2]), v2))
    #             found_dmg.add(k2)
    #         else:
    #             output.write('{}: [{}], '.format(k2, v2))
    #     for k2, v2 in sorted(d1.items(), key=lambda item: item[0]):
    #         if k2 not in found_dmg:
    #             output.write('{}: {:d}, '.format(k2, int(v2)))

def compile_stats(real_d, adv, do_buffs=True):
    # aff uptimes
    stat_str = adv.stats or []
    for aff, up in adv.afflics.get_uptimes().items():
        stat_str.append(f'{aff}:{up:.1%}')
    if not do_buffs:
        return ';'.join(stat_str)
    if adv.logs.team_buff > 0:
        stat_str.append(f'team:{adv.logs.team_buff/real_d:.5%}')
    if adv.logs.team_doublebuffs > 0:
        stat_str.append(f'doublebuff:every {real_d/adv.logs.team_doublebuffs:.2f}s')
    for k, v in adv.logs.team_tension.items():
        stat_str.append(f'{k}:{int(v)}')
    return ';'.join(stat_str)

def summation(real_d, adv, output, cond=True):
    res = dps_sum(real_d, adv.logs.damage)
    if cond:
        output.write('='*BR+'\n')
        output.write('DPS - {}'.format(round(res['dps'])))
        if adv.logs.team_buff > 0:
            output.write(' (team: {:.2f})'.format(adv.logs.team_buff / real_d))
        if adv.logs.team_doublebuffs > 0:
            output.write(' (dbiv: {:.1f}s)'.format(real_d/adv.logs.team_doublebuffs))
        for k, v in adv.logs.team_tension.items():
            output.write(' ({}: {})'.format(k, int(v)))
        # if no_cond_dps:
        #     output.write(' | {}'.format(no_cond_dps['dps']))
        #     if no_cond_dps['team_buff'] > 0:
        #         output.write(' (team: {:.2f})'.format(no_cond_dps['team_buff']))
        #     for k, v in no_cond_dps['team_tension'].items():
        #         output.write(' ({}: {})'.format(k, int(v)))
        output.write(', duration {:.2f}s'.format(real_d))

        output.write('\n')
        output.write(adv.slots.c.name)
        output.write(' ')
        output.write(slots(adv))
        output.write('\n')
        cond_comment = []
        if adv.condition.exist():
            cond_comment.append('<{}>'.format(adv.condition.cond_str()))
        if len(adv.comment) > 0:
            cond_comment.append(adv.comment)
        affstr = compile_stats(real_d, adv, do_buffs=False)
        if affstr:
            cond_comment.append('|')
            cond_comment.append(affstr)
        if len(cond_comment) > 0:
            output.write(' '.join(cond_comment))
            output.write('\n')
    output.write('-'*BR)
    damage_counts(real_d, adv.logs.damage, adv.logs.counts, output, res=res)
    output.write('\n')

XN_PATTERN = re.compile(r'^x\d')
def report(real_d, adv, output, cond=True, web=False):
    name = adv.name
    dmg = adv.logs.damage
    res = dps_sum(real_d, dmg)
    report_csv = [res['dps']]
    report_csv.extend([
        *slots_csv(adv, web),
        adv.condition.cond_str(),
        adv.comment if not web else adv.comment.replace(',', '&comma;'),
        compile_stats(real_d, adv)
    ])

    dps_mappings = {}
    for k in sorted(dmg['x']):
        base_k = XN_PATTERN.sub('x', k)
        try:
            dps_mappings[base_k] += dmg['x'][k] / real_d
        except KeyError:
            dps_mappings[base_k] = dmg['x'][k] / real_d
    for k in sorted(dmg['f']):
        dps_mappings[k] = dmg['f'][k] / real_d
    for k in sorted(dmg['s']):
        dps_mappings[k] = dmg['s'][k] / real_d
    # if buff > 0:
    #     dps_mappings['team_buff'] = buff*team_dps
    #     report_csv[0] += dps_mappings['team_buff']
    # for tension, count in adv.logs.team_tension.items():
    #     dmg_val = count*skill_efficiency(real_d, team_dps, tension_efficiency[tension])
    #     if dmg_val > 0:
    #         dps_mappings['team_{}'.format(tension)] = dmg_val
    #         report_csv[0] += dmg_val
    for k in sorted(dmg['o']):
        dmg_val = dmg['o'][k]
        if dmg_val > 0:
            dps_mappings[k] = dmg_val / real_d
    for k in sorted(dmg['d'], reverse=True):
        dmg_val = dmg['d'][k]
        if dmg_val > 0:
            if k.startswith('dx') or k == 'dshift':
                k = 'dx'
            try:
                dps_mappings[k] += dmg_val / real_d
            except:
                dps_mappings[k] = dmg_val / real_d

    report_csv[0] = round(report_csv[0])
    report_csv.extend(['{}:{}'.format(k, int(v)) for k, v in dps_mappings.items()])

    output.write(','.join([str(s) for s in report_csv]))
    output.write('\n')
    return report_csv


def same_build_different_dps(a, b):
    return all([a[k] == b[k] for k in ('slots.a', 'slots.d', 'acl', 'coabs', 'share')]) and any([a[k] != b[k] for k in ('dps', 'team')])

BANNED_PRINTS = ('Witchs_Kitchen', 'Berry_Lovable_Friends', 'Happier_Times', 'United_by_One_Vision', 'Second_Anniversary')
ABNORMAL_COND = ('sim_buffbot', 'dragonbattle', 'classbane', 'hp', 'dumb', 'afflict_res')
BUFFER_THRESHOLD = 35000
TDPS_WEIGHT = 15000
def save_equip(adv, real_d, repair=False, etype=None):
    adv.duration = int(adv.duration)
    if adv.duration not in (60, 120, 180):
        return
    if any([k in adv.conf for k in ABNORMAL_COND]):
        return
    if any([wp in BANNED_PRINTS for wp in adv.slots.a.qual_lst]):
        return
    etype = etype or 'base'
    eleaff = core.simulate.ELE_AFFLICT[adv.slots.c.ele]
    if adv.sim_afflict:
        if adv.sim_afflict != {eleaff} or \
           adv.conf_init.sim_afflict[eleaff] != 1:
            return
        else:
            etype = etype if repair else 'affliction'
    dkey = str(adv.duration)
    adv_qual = adv.name
    equip = load_equip_json(adv_qual)
    cached = None
    acl_list = adv.conf.acl
    if not isinstance(acl_list, list):
        acl_list = [line.strip() for line in acl_list.split('\n') if line.strip()]
    ndps = sum(map(lambda v: sum(v.values()), adv.logs.damage.values())) / real_d
    nteam = adv.logs.team_buff / real_d
    new_equip = {
        'dps': ndps,
        'team': nteam,
        'tdps': None,
        'slots.a': adv.slots.a.qual_lst,
        'slots.d': adv.slots.d.qual,
        'acl': acl_list,
        'coabs': adv.slots.c.coab_list,
        'share': adv.skillshare_list
    }
    try:
        cached = equip[dkey][etype]
        cdps = cached.get('dps', 0)
        cteam = cached.get('team', 0)
        repair = repair or same_build_different_dps(cached, new_equip)
    except KeyError:
        try:
            cached = equip[dkey]['base']
            cdps = cached.get('dps', 0)
            cteam = cached.get('team', 0)
            repair = repair or same_build_different_dps(cached, new_equip)
        except KeyError:
            cdps = 0
            cteam = 0
    ncomp = ndps + nteam * TDPS_WEIGHT
    ccomp = cdps + cteam * TDPS_WEIGHT
    if not repair and ncomp < ccomp:
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
    if not repair and (etype == 'base' and nteam < cteam and 'buffer' not in equip[dkey]):
        equip[dkey]['buffer'] = cached
        equip[dkey]['buffer']['tdps'] = (ndps - cdps) / (cteam - nteam)
    if dkey not in equip:
        equip[dkey] = {}
    equip[dkey][etype] = new_equip
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
        try:
            equip[dkey]['buffer']['tdps'] = dps_delta / team_delta
        except ZeroDivisionError:
            equip[dkey]['buffer']['tdps'] = 99999999
    except KeyError:
        pass
    if 'buffer' in equip[dkey] and equip[dkey]['buffer']['tdps'] < BUFFER_THRESHOLD:
        equip[dkey]['pref'] = 'buffer'
        equip[dkey]['base']['tdps'] = equip[dkey]['buffer']['tdps']
    else:
        equip[dkey]['pref'] = 'base'
    save_equip_json(adv_qual, equip)

CAP_SNEK = re.compile(r'(^[a-z]|_[a-z])')
def cap_snakey(name):
    return CAP_SNEK.sub(lambda s: s.group(1).upper(), name)

def load_adv_module(name, in_place=None):
    parts = os.path.basename(name).split('.')
    vkey = None if len(parts) == 1 else parts[1].upper()
    name = cap_snakey(parts[0])
    lname = name.lower()
    try:
        advmodule = getattr(__import__(f'adv.{lname}'), lname)
        if in_place is not None:
            in_place[name] = advmodule.variants
            return
        try:
            loaded = advmodule.variants[vkey]
        except KeyError:
            loaded = advmodule.variants[None]
        return loaded, name
    except ModuleNotFoundError:
        if in_place is not None:
            in_place[name] =  {None: core.advbase.Adv}
            return
        return core.advbase.Adv, name

def test_with_argv(*argv):
    if argv[0] is not None and not isinstance(argv[0], str):
        module = argv[0]
    else:
        module, name = load_adv_module(argv[1])
    try:
        verbose = int(argv[2])
    except:
        verbose = 0
    try:
        duration = int(argv[3])
    except:
        duration = 180
    try:
        mass = int(argv[4])
    except:
        mass = 0
    test(name, module, verbose=verbose, duration=duration, mass=mass)

if __name__ == '__main__':
    test_with_argv(*sys.argv)
