import os
import json
import argparse
import glob
from posixpath import basename
from time import monotonic, time_ns

import core.simulate
from conf import ROOT_DIR, load_adv_json, list_advs, ELEMENTS, WEAPON_TYPES, DURATIONS, SKIP_VARIANT
from conf.equip import get_equip_manager, ALL_COND_ENUMS, ConditionTuple
import itertools

ADV_DIR = "adv"
CHART_DIR = "www/dl-sim"
CHARA_DIR = os.path.join(ROOT_DIR, CHART_DIR, "chara")


def printlog(prefix, delta, advname, variant, err=None, color=None):
    if variant:
        logstr = f"{delta:.4f}s - {prefix}:{advname}.{variant}"
    else:
        logstr = f"{delta:.4f}s - {prefix}:{advname}"
    if err:
        logstr += f" {err!r}"
    if color:
        logstr = f"\033[{color}m{logstr}\033[0m"
    print(logstr, flush=True)


def dps_values(filename):
    dps = {}
    try:
        with open(filename, "r") as f:
            for k, v in json.load(f).items():
                dps[k] = v.get("dps", 0)
    except Exception:
        return dps
    return dict(sorted(dps.items()))


def sim_adv(name, variants, sanity_test=False):
    t_start = monotonic()
    is_mass = "mass" in variants
    msg = []
    duration = 180
    for variant, advmodule in variants.items():
        if variant in SKIP_VARIANT:
            continue
        if advmodule.NO_DEPLOY:
            continue
        verbose = -5
        outfile = None
        outpath = None
        mass = 1000 if is_mass and not sanity_test else None
        if sanity_test:
            duration = 10
            outpath = os.devnull
        else:
            if variant is None:
                outfile = f"{name}.json"
            else:
                outfile = f"{name}.{variant}.json"
            outpath = os.path.join(ROOT_DIR, CHART_DIR, "chara", outfile)
        dps_before = dps_values(outpath)
        with open(outpath, "w") as output:
            try:
                core.simulate.test(
                    name,
                    advmodule,
                    duration=duration,
                    verbose=verbose,
                    mass=mass,
                    output=output,
                )
            except Exception as e:
                printlog("sim", monotonic() - t_start, name, variant, err=e, color=91)
                # raise e
                return []
        if not sanity_test:
            dps_after = dps_values(outpath)
            printlog("sim", monotonic() - t_start, name, variant)
            if dps_before != dps_after:
                msg.append(name)
                print(dps_before)
                print(dps_after)
    if sanity_test:
        for variant_equip in glob.glob(os.path.join(ROOT_DIR, f"conf/equip/{name}.*.json")):
            if os.path.basename(variant_equip).split(".")[1] not in variants:
                os.remove(variant_equip)
                print("pruned", variant_equip)
    return msg


ELE_IDX = {
    "flame": 0,
    "water": 1,
    "wind": 2,
    "light": 3,
    "shadow": 4,
}


def msg_sort(adv):
    advconf = load_adv_json(adv)
    return ELE_IDX[advconf["c"]["ele"]], adv


def combine():
    t_start = monotonic()
    # check what adv jsons we should have
    expected_jsons = set()
    for name, variants in get_sim_target_module_dict().items():
        for variant, module in variants.items():
            if variant is None:
                expected_jsons.add(name)
            elif variant not in SKIP_VARIANT and not module.NO_DEPLOY:
                expected_jsons.add(f"{name}.{variant}")
    # do combine
    data_by_cond = {str(ConditionTuple(cond)): {} for cond in itertools.product(*ALL_COND_ENUMS)}
    # ConditionTuple
    for fn in os.listdir(CHARA_DIR):
        name, ext = os.path.splitext(fn)
        if not ext == ".json":
            continue

        chara_json = os.path.join(CHARA_DIR, fn)
        if name not in expected_jsons:
            os.remove(chara_json)
            print("pruned", fn)
            continue

        with open(chara_json, "r") as chara:
            try:
                chara_sim = json.load(chara)
            except json.JSONDecodeError as e:
                print(chara_json)
                raise e
            for condstr, result in chara_sim.items():
                data_by_cond[condstr][name] = result

    for condstr, results in data_by_cond.items():
        with open(os.path.join(ROOT_DIR, CHART_DIR, f"page/{condstr}.json"), "w") as f:
            json.dump(results, f, separators=(",", ":"))

    with open(os.path.join(ROOT_DIR, CHART_DIR, "page/lastmodified.json"), "r+") as f:
        try:
            lastmod = json.load(f)
        except:
            lastmod = {}
        f.truncate(0)
        f.seek(0)
        lastmod["timestamp"] = time_ns() // 1000000
        try:
            sort_message = sorted(set(lastmod["changed"]), key=msg_sort)
            lastmod["message"] = list(sort_message)
            del lastmod["changed"]
        except KeyError:
            lastmod["message"] = []
        json.dump(lastmod, f)

    print(f"{monotonic() - t_start:.4f}s - combine", flush=True)


def get_sim_target_module_dict(advs=None, conds=None, mass=None, special=False):
    target_modules = {}
    advs = advs or list_advs()
    for adv in advs:
        try:
            name = core.simulate.load_adv_module(adv, in_place=target_modules)
            if conds is not None:
                adv_data = load_adv_json(name)
                if not all([cond(adv_data) for cond in conds]):
                    del target_modules[name]
                    continue
            if mass is not None:
                if (mass and "mass" not in target_modules[name]) or (not mass and "mass" in target_modules[name]):
                    del target_modules[name]
                    continue
            if special and all((variant == None or variant in SKIP_VARIANT for variant in target_modules[name].keys())):
                del target_modules[name]
                continue
        except Exception as e:
            printlog("load", monotonic() - t_start, adv, None, err=e, color=93)
    return target_modules


def get_sim_target_modules(targets):
    target_filters = set()
    target_advs = set()
    target_kind = set()
    for target in targets:
        if target in ("all", "quick", "slow", "special"):
            target_kind.add(target)
        elif target in ELEMENTS:
            element = str(target)
            target_filters.add(lambda d: d["c"]["ele"] == element)
        elif target in WEAPON_TYPES:
            weapontype = str(target)
            target_filters.add(lambda d: d["c"]["wt"] == weapontype)
        else:
            target_advs.add(target)
    special = "special" in target_kind
    if "quick" in target_kind:
        return get_sim_target_module_dict(target_advs, target_filters, mass=False, special=special)
    if "slow" in target_kind:
        return get_sim_target_module_dict(target_advs, target_filters, mass=True, special=special)
    return get_sim_target_module_dict(target_advs, target_filters, special=special)


def main(targets, do_combine, is_repair, sanity_test):
    if targets:
        target_modules = get_sim_target_modules(targets)
        if not target_modules:
            exit()

        if is_repair:
            for advname, variants in target_modules.items():
                for variant, advmodule in variants.items():
                    t_start = monotonic()
                    manager = get_equip_manager(advname, variant, advmodule.SAVE_VARIANT)
                    if manager._save:
                        manager.repair_entries(advmodule)
                        printlog("repair", monotonic() - t_start, advname, variant)
            return

        message = []
        for name, variants in target_modules.items():
            message.extend(sim_adv(name, variants, sanity_test=sanity_test))

        if sanity_test:
            return

        with open(os.path.join(ROOT_DIR, CHART_DIR, "page/lastmodified.json"), "r+") as f:
            try:
                lastmod = json.load(f)
            except:
                lastmod = {}
            f.truncate(0)
            f.seek(0)
            try:
                lastmod["changed"].extend(message)
            except KeyError:
                lastmod["changed"] = message
            json.dump(lastmod, f)

    if do_combine:
        combine()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy adventurers.")
    parser.add_argument(
        "targets",
        type=str,
        nargs="*",
        help="""targets to simulate:
    all: all advs
    quick: not mass sim advs
    slow: mass sim advs
    special: variant sims
    [element]: [element] attribute advs
    [weapon]: [weapon] type advs
    [qual_name]: adv names""",
    )
    parser.add_argument("-combine", "-c", help="run combine after sim", action="store_true")
    parser.add_argument("-repair", "-rp", help="run equip.json repair", action="store_true")
    parser.add_argument("-sanity_test", "-san", help="run sanity test only", action="store_true")
    args = parser.parse_args()

    t_start = monotonic()
    main(args.targets, args.combine, args.repair, args.sanity_test)
    print("total: {:.4f}s".format(monotonic() - t_start))
