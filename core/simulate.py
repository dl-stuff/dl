import sys
import os
import re
import json
from collections import defaultdict, Counter
from conf.equip import (
    AfflictionCondition,
    MonoCondition,
    SituationCondition,
    ConditionTuple,
    DEFAULT_CONDITONS,
    str_to_equip_condition,
    all_monoele_coabs,
)

from conf import DRG, get_icon, get_fullname
import core.acl
import core.advbase

BR = 64


def run_once(name, module, conf, duration, equip_conditions=None, opt_mode=None):
    adv = module(name=name, conf=conf, duration=duration, equip_conditions=equip_conditions, opt_mode=opt_mode)
    real_d = adv.run()
    return adv, real_d


# Using starmap
import multiprocessing


def run_once_mass(name, module, conf, duration, equip_conditions, opt_mode, idx):
    adv = module(name=name, conf=conf, duration=duration, equip_conditions=equip_conditions, opt_mode=opt_mode)
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


def run_mass(mass, base_log, base_d, name, module, conf, duration, equip_conditions=None, opt_mode=None):
    adv_2, real_d_2 = run_once(name, module, conf, duration, equip_conditions=equip_conditions, opt_mode=opt_mode)
    if adv_2.logs.damage == base_log.damage:
        return base_log, base_d
    else:
        base_log = sum_logs(base_log, adv_2.logs)
        base_d += real_d_2

    mass = 500 if mass == 1 else mass
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        for log, real_d in pool.starmap(
            run_once_mass,
            [(name, module, conf, duration, equip_conditions, opt_mode, idx) for idx in range(mass - 2)],
        ):
            base_log = sum_logs(base_log, log)
            base_d += real_d
    base_log = avg_logs(base_log, mass)
    base_d /= mass
    return base_log, base_d


# def run_variants_with_conf(run_results, name, module, conf, duration, cond, mass, equip_conditions, variant, deploy_mono, manager):
#     adv, real_d = run_once(name, module, conf, duration, cond, equip_conditions=equip_conditions)
#     if mass:
#         adv.logs, real_d = run_mass(
#             mass,
#             adv.logs,
#             real_d,
#             name,
#             module,
#             conf,
#             duration,
#             cond,
#             equip_conditions=equip_conditions,
#         )
#     run_results.append((adv, real_d, variant, None))
#     if deploy_mono:
#         if manager.has_different_mono(180, adv.equip_key):
#             adv, real_d = run_once(name, module, conf, duration, cond, equip_key=None, mono=True)
#             if mass:
#                 adv.logs, real_d = run_mass(
#                     mass,
#                     adv.logs,
#                     real_d,
#                     name,
#                     module,
#                     conf,
#                     duration,
#                     cond,
#                     equip_conditions=adv.equip_conditions.to_any(),
#                 )
#         run_results.append((adv, real_d, variant, "mono"))
#     return adv, real_d


def run_once_and_mass(name, module, conf, duration, mass, equip_conditions, opt_mode, result_by_cond):
    adv, real_d = run_once(name, module, conf, duration, equip_conditions=equip_conditions, opt_mode=opt_mode)
    if mass:
        adv.logs, real_d = run_mass(mass, adv.logs, real_d, name, module, conf, duration, equip_conditions=equip_conditions, opt_mode=opt_mode)
    adv.equip_manager.accept_new_entry(adv, real_d)
    result_by_cond[str(equip_conditions)] = report(adv, real_d)
    return adv, real_d


def test(name, module, conf={}, duration=180, verbose=0, mass=None, output=sys.stdout, equip_conditions=None, opt_mode=None):
    if verbose == 2:
        # output.write(adv._acl_str)
        adv = module(name=name)
        output.write(str(core.acl.build_acl(adv.conf.acl)._acl_str))
        output.write(str(core.acl.build_acl(adv.conf.acl)._tree.pretty()))
        return
    if verbose == -5:
        equip_conditions = DEFAULT_CONDITONS
    adv, real_d = run_once(name, module, conf, duration, equip_conditions=equip_conditions, opt_mode=opt_mode)
    if verbose == 1:
        adv.logs.write_logs(output=output)
        act_sum(adv.logs.act_seq, output)
        return
    if verbose == 4:
        return adv, real_d
    if verbose == 5:
        return adv, real_d, report(adv, real_d)
    if mass:
        adv.logs, real_d = run_mass(mass, adv.logs, real_d, name, module, conf, duration, equip_conditions=equip_conditions, opt_mode=opt_mode)
    if verbose == -2:
        report(adv, real_d, output)
        return
    if verbose == -5 or verbose == -25:
        adv.equip_manager.accept_new_entry(adv, real_d)
        result_by_cond = {str(DEFAULT_CONDITONS): report(adv, real_d)}
        for sit in SituationCondition:
            aff = AfflictionCondition.SELF
            econd_base = ConditionTuple((aff, sit, MonoCondition.ANY))
            if econd_base != DEFAULT_CONDITONS:
                adv, real_d = run_once_and_mass(name, module, conf, duration, mass, econd_base, opt_mode, result_by_cond)
            econd_mono = ConditionTuple((aff, sit, MonoCondition.MONO))
            if adv.equip_manager[econd_mono].empty:
                if all_monoele_coabs(adv.slots.c.ele, result_by_cond[str(econd_base)]["coabs"]):
                    result_by_cond[str(econd_mono)] = result_by_cond[str(econd_base)]
            else:
                run_once_and_mass(name, module, conf, duration, mass, econd_mono, opt_mode, result_by_cond)

            noaff = adv.uses_affliction()
            for aff in (AfflictionCondition.ALWAYS, AfflictionCondition.IMMUNE):
                aff_econd_base = ConditionTuple((aff, sit, MonoCondition.ANY))
                if adv.equip_manager[aff_econd_base].empty and noaff:
                    result_by_cond[str(aff_econd_base)] = result_by_cond[str(econd_base)]
                else:
                    run_once_and_mass(name, module, conf, duration, mass, aff_econd_base, opt_mode, result_by_cond)
                aff_econd_mono = ConditionTuple((aff, sit, MonoCondition.MONO))
                if adv.equip_manager[aff_econd_mono].empty:
                    if all_monoele_coabs(adv.slots.c.ele, result_by_cond[str(aff_econd_base)]["coabs"]):
                        result_by_cond[str(aff_econd_mono)] = result_by_cond[str(aff_econd_base)]
                else:
                    run_once_and_mass(name, module, conf, duration, mass, aff_econd_mono, opt_mode, result_by_cond)

        if verbose == -25:
            # json.dump(result_by_cond, output, indent=4)
            for cond, report_dict in result_by_cond.items():
                condstr = str(cond)
                width = BR - 3 - len(condstr)
                output.write("\n={")
                output.write(str(cond))
                output.write("}")
                output.write("=" * width)
                output.write("\n")
                write_readable_report(report_dict, output)
        else:
            json.dump(result_by_cond, output, separators=(",", ":"))
        return
    summation(adv, real_d, output)


def slots(adv):
    slots = f"[{adv.slots.d}][{adv.slots.w}][{adv.slots.a}]\n"
    slots += "-" * (len(adv.name)) + " "
    slots += f'[{"|".join((map(get_fullname, adv.slots.c.coab_list)))}][S3:{get_fullname(adv.skillshare_list[0])}'
    try:
        slots += f"|S4:{get_fullname(adv.skillshare_list[1])}]"
    except:
        slots += "]"
    return slots


def append_condensed(condensed, act):
    if len(condensed) > 0:
        l_act, l_cnt = condensed[-1]
        if l_act == act:
            condensed[-1] = (l_act, l_cnt + 1)
            return condensed
    condensed.append((act, 1))
    return condensed


def act_repeats(condensed):
    condensed = list(filter(lambda a: not a[0].startswith(DRG), condensed))
    start = 0
    maxlen = len(condensed)
    bestest = condensed, 1, 0
    for start in range(0, maxlen):
        accumulator = Counter()
        length = 1
        c_slice = tuple(condensed[start : start + length])
        while start + length * (accumulator[c_slice] + 1) <= maxlen:
            n_slice = tuple(condensed[start + length * accumulator[c_slice] : start + length * (accumulator[c_slice] + 1)])
            if n_slice == c_slice:
                accumulator[c_slice] += 1
            else:
                length += 1
                c_slice = tuple(condensed[start : start + length])
                accumulator[c_slice] = 1
        c_best = accumulator.most_common(1)
        if len(c_best) > 0 and c_best[0][1] > bestest[1]:
            bestest = (*c_best[0], start)
    return bestest


def act_sum(actions, output):
    p_act = "_"
    p_xseq = 0
    condensed = []
    for act in actions:
        act1 = act.split("_")[0]
        if act[0] == "x":
            xseq = int(act1[1:])
            if xseq <= p_xseq:
                condensed = append_condensed(condensed, p_act)
            p_xseq = xseq
        elif (act.startswith("fs") or act == "d") and p_act[0] == "x":
            p_xseq = 0
            condensed = append_condensed(condensed, p_act + act1)
        else:
            if p_act[0] == "x":
                condensed = append_condensed(condensed, p_act)
            p_xseq = 0
            condensed = append_condensed(condensed, act)
        p_act = act1
    if p_act[0] == "x":
        condensed = append_condensed(condensed, p_act)
    seq, freq, start = act_repeats(condensed)
    seqlen = len(seq)
    if freq < 2 or freq * seqlen < len(condensed) // 4:
        seqlen = 24
        freq = len(condensed) // seqlen
        start = 0
    p_type = None
    idx_offset = 0
    for idx, ac in enumerate(condensed):
        act, cnt = ac
        idx = idx - idx_offset
        if start > idx > 0 and idx % 12 == 0:
            output.write("\n")
        elif freq >= 0 and start < idx and (idx - start) % seqlen == 0:
            output.write("\n")
            freq -= 1
        elif idx > 0:
            output.write(" ")
        if act[0] == "x" or act.startswith("fs"):
            if act[0] == "x":
                act = "c" + act[1:]
            if act[:2] == "fs":
                parts = act.split("_")
                if len(parts) > 1:
                    act = act.split("_")[0] + "-" + parts[1][0]
            output.write(act)
            p_type = "x"
        else:
            parts = act.split("_")
            if len(parts) > 1:
                if parts[1][:5] == "phase":
                    act = parts[0] + "-" + parts[1][-1]
                else:
                    act = parts[0] + "-" + parts[1]
            output.write("[" + act + "]")
            p_type = "s"
        if cnt > 1:
            output.write("*{}".format(cnt))


def dps_sum(damage, real_d):
    res = {"dps": 0}
    for k, v in damage.items():
        ds = dict_sum(v)
        res[k] = ds / real_d
        res["dps"] += ds
    res["dps"] = res["dps"] / real_d
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
    ck = k.split("_")
    return "x" if len(ck) == 1 else f"x_{ck[1]}"


def d_rule(k):
    return "dx" if k.startswith("dx") else k


def damage_counts(real_d, damage, counts, output, res=None):
    if res is None:
        res = dps_sum(real_d, damage)
    found_dmg = set()
    for k1 in damage.keys():
        dmg = damage.get(k1)
        cnt = counts.get(k1)
        if dmg or cnt:
            if res["dps"] == 0:
                output.write("\n{:>1} {:>3.0f}| ".format(k1, 0))
            else:
                output.write("\n{:>1} {:>3.0f}%| ".format(k1, res[k1] * 100 / res["dps"]))
        if k1 == "x":
            dmg, cnt = condense_damage_counts(dmg, cnt, x_rule)
        if k1 == "d":
            dmg, cnt = condense_damage_counts(dmg, cnt, d_rule)
        for k2, v2 in sorted(cnt.items(), key=lambda item: item[0]):
            if dmg.get(k2):
                output.write("{}: {:d} [{}], ".format(k2, int(dmg[k2]), v2))
                found_dmg.add(k2)
            else:
                output.write("{}: [{}], ".format(k2, v2))
        for k2, v2 in sorted(dmg.items(), key=lambda item: item[0]):
            if k2 not in found_dmg:
                output.write("{}: {:d}, ".format(k2, int(v2)))

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


def compile_stats(adv, real_d):
    stats = {}
    for aff, up in adv.afflics.get_uptimes():
        stats[aff] = f"{up:.1%}"
    if adv.logs.team_doublebuffs > 0:
        stats["doublebuff"] = f"every {real_d / adv.logs.team_doublebuffs:.2f}s"
    for amp_name, timings in adv.logs.team_amp_publish.items():
        amp_key = f"team_{amp_name}"
        first_time = min(timings)
        stats[amp_key] = f"from {first_time:.2f}s"
        if len(timings) > 1:
            avg_iv = (max(timings) - first_time) / (len(timings) - 1)
            stats[amp_key] = f"every {avg_iv:.2f}s " + stats[amp_key]
        else:
            stats[amp_key] = "1 time " + stats[amp_key]
    for k, v in adv.logs.team_tension.items():
        stats[k] = int(v)
    return stats


def summation(adv, real_d, output):
    res = dps_sum(adv.logs.damage, real_d)
    output.write("=" * BR + "\n")
    output.write("DPS - {}".format(round(res["dps"])))
    output.write(", duration {:.2f}s".format(real_d))

    if adv.logs.heal:
        output.write("\nHealing - ")
        for k, v in adv.logs.heal.items():
            output.write("{}: {}; ".format(k, int(v)))

    output.write("\n")
    output.write(adv.slots.c.name)
    output.write(" ")
    output.write(slots(adv))
    output.write("\n")
    cond_comment = []
    if adv.condition.exist():
        cond_comment.append("<{}>".format(adv.condition.cond_str()))
    if len(adv.comment) > 0:
        cond_comment.append(adv.comment)
    stats = compile_stats(adv, real_d)
    if stats:
        cond_comment.append("|")
        cond_comment.append(";".join((f"{k}:{v}" for k, v in stats.items())))
    if len(cond_comment) > 0:
        output.write(" ".join(cond_comment))
        output.write("\n")
    output.write("-" * BR)
    damage_counts(real_d, adv.logs.damage, adv.logs.counts, output, res=res)
    output.write("\n")


XN_PATTERN = re.compile(r"^x\d")


def write_readable_report(report_dict, output):
    for key, value in report_dict.items():
        key = key.ljust(9)
        output.write(key)
        output.write(f"{value!r}")
        output.write("\n")


def report(adv, real_d, output=None):
    report_dict = {
        "equip": str(adv.real_equip_conditions),
        "adv": adv.slots.c.qual,
        "ele": adv.slots.c.ele,
        "wt": adv.slots.c.wt,
        "variant": adv.variant,
        "drg": adv.slots.d.qual,
        "wep": adv.slots.w.qual,
        "wps": adv.slots.a.qual_lst,
        "coabs": adv.slots.c.coab_list,
        "share": adv.skillshare_list,
        "cond": adv.condition.cond_str(),
        "comment": adv.comment,
        "real": round(real_d, 2),
    }
    if not report_dict["variant"]:
        del report_dict["variant"]
    dmg = adv.logs.damage
    report_dict["dps"] = int(dps_sum(dmg, real_d)["dps"])
    report_dict["team"] = adv.logs.team_buff / real_d
    dps_mappings = {}
    for k in sorted(dmg["x"]):
        base_k = XN_PATTERN.sub("x", k)
        try:
            dps_mappings[base_k] += dmg["x"][k] / real_d
        except KeyError:
            dps_mappings[base_k] = dmg["x"][k] / real_d
    for k in sorted(dmg["f"]):
        dps_mappings[k] = dmg["f"][k] / real_d
    for k in sorted(dmg["s"]):
        dps_mappings[k] = dmg["s"][k] / real_d
    for k in sorted(dmg["o"]):
        dmg_val = dmg["o"][k]
        if dmg_val > 0:
            dps_mappings[k] = dmg_val / real_d
    for k in sorted(dmg["d"], reverse=True):
        dmg_val = dmg["d"][k]
        if dmg_val > 0:
            if k.startswith("dx") or k == "dshift":
                k = "dx"
            if k == "ds_final":
                k = "ds"
            try:
                dps_mappings[k] += dmg_val / real_d
            except:
                dps_mappings[k] = dmg_val / real_d
    report_dict["slices"] = [(k, int(v)) for k, v in dps_mappings.items()]
    stats = compile_stats(adv, real_d)
    if stats:
        report_dict["stats"] = stats

    if output:
        write_readable_report(report_dict, output)
    else:
        return report_dict


CAP_SNEK = re.compile(r"(^[a-z]|_[a-z])")


def cap_snakey(name):
    return CAP_SNEK.sub(lambda s: s.group(1).upper(), name)


def load_adv_module(name, in_place=None):
    parts = os.path.basename(name).split(".")
    vkey = None if len(parts) == 1 else parts[1].upper()
    name = cap_snakey(parts[0])
    lname = name.lower()
    try:
        advmodule = getattr(__import__(f"adv.{lname}"), lname)
        if in_place is not None:
            in_place[name] = advmodule.variants
            return name
        try:
            loaded = advmodule.variants[vkey]
        except KeyError:
            vkey = None
            loaded = advmodule.variants[None]
        return loaded, name, vkey
    except ModuleNotFoundError:
        if in_place is not None:
            in_place[name] = {None: core.advbase.Adv}
            return name
        return core.advbase.Adv, name, None


def test_with_argv(*argv):
    if argv[0] is not None and not isinstance(argv[0], str):
        module = argv[0]
    else:
        module, name, variant = load_adv_module(argv[1])
    try:
        verbose = int(argv[2])
    except:
        verbose = 0
    try:
        duration = int(argv[3])
    except:
        duration = 180
    try:
        equip = str_to_equip_condition(argv[4])
    except:
        equip = None
    test(name, module, verbose=verbose, duration=duration, equip_conditions=equip)


if __name__ == "__main__":
    test_with_argv(*sys.argv)
