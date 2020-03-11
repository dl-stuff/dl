import sys
import os

BR = 64
BLADE = 1.10
WAND = 1.15
def skill_efficiency(real_d, team_dps, mod):
    return (team_dps * 1.25) * mod * 2 / 5 / real_d
tension_efficiency = {
    'energy': 0.5,
    'inspiration': 0.6
}
ex_mapping = {
    'k': 'blade',
    'r': 'wand',
    'd': 'dagger',
    'b': 'bow',
    'm': 'axe2',
    's': 'sword',
    'g': 'geuden'
}

def blade_mod(name, value):
    return value * BLADE

def wand_mod(name, value):
    if name[0] == 's' or name == 'ds':
        return value * WAND
    else:
        return value

def blade_wand_mod(name, value):
    return blade_mod(name, wand_mod(name, value))

def parse_ex(ex):
    ex_set = {}
    for e in ex:
        try:
            ex_name = ex_mapping[e]
            ex_set[ex_name] = ('ex', ex_name)
        except:
            continue
    return ex_set

def build_exp_mod_list(ex, ex_set, wt):
    if ex == '_':
        ex = ''
        ex_mod_func = [('_', None)]
    else:
        ex_mod_func = [('', None)]
    if 'blade' not in ex_set and wt != 'blade':
        ex_mod_func.append(('k', blade_mod))
        has_k = True
    else:
        ex_mod_func.append(('k', None))
        has_k = False
    if 'wand' not in ex_set and wt != 'wand':
        ex_mod_func.append(('r', wand_mod))
        has_r = True
    else:
        ex_mod_func.append(('r', None))
        has_r = False
    if has_k and has_r:
        ex_mod_func.append(('kr', blade_wand_mod))
    elif has_k:
        ex_mod_func.append(('kr', blade_mod))
    elif has_r:
        ex_mod_func.append(('kr', wand_mod))
    else:
        ex_mod_func.append(('kr', None))
    return ex_mod_func, ex

def test(classname, conf={}, ex='_', duration=180, verbose=0, mass=None, special=False, output=None):
    output = output or sys.stdout
    ex_set = parse_ex(ex)
    if len(ex_set) > 0:
        conf['ex'] = ex_set
    else:
        ex = '_'
    run_results = []
    adv = classname(conf=conf,cond=True)
    real_d = adv.run(duration)
    if verbose == 1:
        adv.logs.write_logs(output=output)
        act_sum(adv.logs.act_seq, output)
        return
    if verbose == 2:
        output.write(adv._acl_str)
        return
    run_results.append((adv, real_d, True))
    no_cond_dps = None
    if adv.condition.exist():
        adv_2 = classname(conf=conf,cond=False)
        real_d_2 = adv_2.run(duration)
        run_results.append((adv_2, real_d_2, False))
        no_cond_dps = round(dps_sum(real_d_2, adv_2.logs.damage)['dps'])

    if verbose == -5:
        ex_mod_func, ex = build_exp_mod_list(ex, ex_set, adv.conf.c.wt)
        page = 'sp' if special else str(duration)
        for ex_str, mod_func in ex_mod_func:
            output.write('-,{},{}{}\n'.format(page, ex_str, ex))
            for a, d, c in run_results:
                report(d, a, output, cond=c, mod_func=mod_func)
    else:
        for a, d, c in run_results:
            if verbose == -2:
                report(d, a, output, cond=c)
            else:
                summation(d, a, output, cond=c, no_cond_dps=no_cond_dps)

def amulets(adv):
    amulets = '['+adv.slots.a.__class__.__name__ + '+' + adv.slots.a.a2.__class__.__name__+']'
    amulets += '['+adv.slots.d.__class__.__name__+']'
    amulets += '['+adv.slots.w.__class__.__name__.split('_')[0]+']'
    return amulets

def append_condensed(condensed, act):
    if len(condensed) > 0:
        l_act, l_cnt = condensed[-1]
        if l_act == act:
            condensed[-1] = (l_act, l_cnt+1)
            return condensed
    condensed.append((act, 1))
    return condensed

def act_sum(actions, output):
    p_act = '_'
    p_xseq = 0
    condensed = []
    for act in actions:
        if act[0] == 'x':
            xseq = int(act[1:])
            if xseq < p_xseq:
                condensed = append_condensed(condensed, p_act)
            p_xseq = xseq
        elif act == 'fs' and p_act[0] == 'x':
            p_xseq = 0
            condensed = append_condensed(condensed, p_act+act)
        else:
            p_xseq = 0
            condensed = append_condensed(condensed, act)
        p_act = act
    if p_act[0] == 'x':
        condensed = append_condensed(condensed, p_act)
    
    p_type = None
    for act, cnt in condensed:
        if act[0] == 'x' or act == 'fs':
            if p_type is None:
                output.write('[  ] ')
            elif p_type != 'd':
                output.write(' ')
            output.write(act.replace('x', 'c'))
            if cnt > 1:
                output.write('*{}'.format(cnt))
            p_type = 'x'
        else:
            if act == 'dshift':
                output.write('\n[-- dragon --]\n')
                p_type == 'd'
            else:
                if p_type == 'x':
                    output.write('\n')
                elif p_type == 's':
                    output.write(' ')
                output.write('['+act+']')
                p_type = 's'

def dps_sum(real_d, damage, mod_func=None):
    res = {'dps':0}
    for k, v in damage.items():
        ds = dict_sum(v, mod_func)
        res[k] = ds / real_d
        res['dps'] += ds
    res['dps'] = res['dps'] / real_d
    return res

def dict_sum(sub, mod_func=None):
    if callable(mod_func):
        return sum([mod_func(k2, v2) for k2, v2 in sub.items()])
    else:
        return sum(sub.values())

def damage_counts(real_d, damage, counts, output, mod_func=None, res=None):
    if res is None:
        res = dps_sum(real_d, damage, mod_func)
    if callable(mod_func):
        mod_func = lambda k, v: round(mod_func(k, v))
    else:
        mod_func = lambda k, v: round(v)
    for k1, v1 in damage.items():
        if len(v1) > 0:
            output.write('\n{:>1} {:02.0f}%| '.format(k1, res[k1] * 100 / res['dps']))
            for k2, v2 in v1.items():
                modded_value = mod_func(k2, v2)
                try:
                    output.write('{}: {:d} [{}], '.format(k2, modded_value, counts[k1][k2]))
                except:
                    output.write('{}: {:d}, '.format(k2, modded_value))

def team(real_d, team_buff):
    t_buff = 0
    p_time, p_buff = 0, 0
    for c_time, c_buff in team_buff:
        t_buff += (c_time - p_time) * p_buff
        p_time, p_buff = c_time, c_buff
    return t_buff / real_d

def summation(real_d, adv, output, cond=True, mod_func=None, no_cond_dps=None):
    res = dps_sum(real_d, adv.logs.damage, mod_func)
    if cond:
        output.write('='*BR+'\n')
        output.write('DPS: {}'.format(round(res['dps'])))
        if no_cond_dps:
            output.write(' | {}'.format(no_cond_dps))
        t_buff = team(real_d, adv.logs.team_buff)
        if t_buff > 0:
            output.write(' (team: {:.2f})'.format(t_buff))
        for k, v in adv.logs.team_tension.items():
            output.write(' ({}: {})'.format(k, int(v)))

        output.write('\n{} (str: {}) {}'.format(
            adv.__class__.__name__, 
            adv.base_att,
            amulets(adv)))
                
        output.write('\n<{}> {}\n'.format(
            adv.condition.cond_str(), 
            adv.comment))
    output.write('-'*BR)
    damage_counts(real_d, adv.logs.damage, adv.logs.counts, output, mod_func=mod_func, res=res)
    if cond:
        output.write('\n')

def report(real_d, adv, output, team_dps=16000, cond=True, mod_func=None):
    name = adv.__class__.__name__
    condition = '<{}>'.format(adv.condition.cond_str())
    dmg = adv.logs.damage
    res = dps_sum(real_d, dmg, mod_func)
    buff = team(real_d, adv.logs.team_buff)
    report_csv = [round(res['dps'])]
    report_csv.extend([
        name if cond else '_c_'+name,
        adv.conf['c.stars']+'*',
        adv.conf['c.ele'],
        adv.conf['c.wt'],
        adv.displayed_att,
        amulets(adv),
        condition if cond else '!' + condition,
        adv.comment
    ])
    dps_mappings = {}
    dps_mappings['attack'] = dict_sum(dmg['x'], mod_func) / real_d
    if 'fs' in dmg['f']:
        dps_mappings['force_strike'] = dmg['f']['fs'] / real_d
    for i, k in enumerate(('s1', 's2', 's3')):
        try:
            dps_mappings['skill_{}'.format(i+1)] = dmg['s'][k] / real_d
        except:
            continue
    if buff > 0:
        dps_mappings['team_buff'] = buff*team_dps
    for tension, count in adv.logs.team_tension.items():
        dmg_val = count*skill_efficiency(real_d, team_dps, tension_efficiency[tension])
        if dmg_val > 0:
            dps_mappings['team_{}'.format(tension)] = dmg_val
    for k, dmg_val in dmg['o'].items():
        if dmg_val > 0:
            dps_mappings[k] = dmg_val / real_d
    for k, dmg_val in dmg['d'].items():
        if dmg_val > 0:
            dps_mappings[k] = dmg_val / real_d

    if callable(mod_func):
        report_csv.extend(['{}:{}'.format(k, round(mod_func(k, v))) for k, v in dps_mappings.items()])
    else:
        report_csv.extend(['{}:{}'.format(k, round(v)) for k, v in dps_mappings.items()])

    output.write(','.join([str(s) for s in report_csv]))
    output.write('\n')
    return report_csv

def load_adv_module(adv_name):
    return getattr(
        __import__('adv.{}'.format(adv_name.lower())),
        adv_name.lower()
    ).module()

if __name__ == '__main__':
    try:
        name = os.path.basename(sys.argv[1]).split('.')[0]
    except:
        name = 'euden'
    try:
        verbose = int(sys.argv[2])
    except:
        verbose = 0
    try:
        duration = int(sys.argv[3])
    except:
        duration = 180
    try:
        ex = sys.argv[4]
    except:
        ex = '_'
    try:
        mass = int(sys.argv[5])
    except:
        mass = 0
    test(load_adv_module(name), verbose=verbose, duration=duration, ex=ex)