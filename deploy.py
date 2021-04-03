import os
import sys
import hashlib
import json
import argparse
from copy import deepcopy
from time import monotonic, time_ns
import core.simulate
from conf import ROOT_DIR, load_adv_json, list_advs, ELEMENTS, WEAPON_TYPES, DURATIONS
from conf.equip import EquipManager

ADV_DIR = "adv"
CHART_DIR = "www/dl-sim"
SKIP_VARIANT = ("RNG", "mass")


def sha256sum(filename):
    if not os.path.exists(filename):
        return None
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, "rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def sim_adv(name, variants, sanity_test=False):
    t_start = monotonic()
    is_mass = "mass" in variants
    msg = []
    for v, adv_module in variants.items():
        if v in SKIP_VARIANT:
            continue
        verbose = -5
        outfile = None
        outpath = None
        mass = 1000 if is_mass and not sanity_test else None
        if sanity_test:
            durations = (30,)
            outpath = os.devnull
        else:
            if v is None:
                durations = DURATIONS
                outfile = f"{name}.csv"
            else:
                durations = (180,)
                outfile = f"{name}.{v}.csv"
            outpath = os.path.join(ROOT_DIR, CHART_DIR, "chara", outfile)
        sha_before = sha256sum(outpath)
        output = open(outpath, "w")
        try:
            for d in durations:
                run_results = core.simulate.test(
                    name,
                    adv_module,
                    {},
                    duration=d,
                    verbose=verbose,
                    mass=mass,
                    special=v is not None,
                    output=output,
                )
            output.close()
            if not sanity_test:
                print(f"{monotonic() - t_start:.4f}s - sim:{name}", flush=True)
                if sha_before != sha256sum(outpath):
                    msg.append(name)
        except Exception as e:
            output.close()
            print(
                f"\033[91m{monotonic()-t_start:.4f}s - sim:{name} {e}\033[0m",
                flush=True,
            )
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

    dst_dict = {}
    pages = [str(d) for d in DURATIONS] + ["mono", "sp"]
    aff = ["_", "affliction", "noaffliction"]
    for p in pages:
        dst_dict[p] = {}
        for a in aff:
            dst_dict[p][a] = open(os.path.join(ROOT_DIR, CHART_DIR, "page/{}_{}.csv".format(p, a)), "w")

    for fn in os.listdir(os.path.join(ROOT_DIR, CHART_DIR, "chara")):
        if not fn.endswith(".csv"):
            continue
        with open(os.path.join(ROOT_DIR, CHART_DIR, "chara", fn), "r", encoding="utf8") as chara:
            for line in chara:
                if line[0] == "-":
                    _, c_page, c_aff = line.strip().split(",")
                else:
                    dst_dict[c_page][c_aff].write(line.strip())
                    dst_dict[c_page][c_aff].write("\n")

    for p in pages:
        for a in aff:
            dst_dict[p][a].close()
            dst_dict[p][a].close()

    with open(os.path.join(ROOT_DIR, CHART_DIR, "page/lastmodified.json"), "r+") as f:
        try:
            lastmod = json.load(f)
        except:
            lastmod = {}
        f.truncate(0)
        f.seek(0)
        lastmod["timestamp"] = time_ns() // 1000000
        try:
            sort_message = [load_adv_json(adv)["c"]["icon"] for adv in sorted(set(lastmod["changed"]), key=msg_sort)]
            lastmod["message"] = list(sort_message)
            del lastmod["changed"]
        except KeyError:
            lastmod["message"] = []
        json.dump(lastmod, f)

    print(f"{monotonic() - t_start:.4f}s - combine", flush=True)


def get_sim_target_module_dict(advs=None, conds=None, mass=None):
    target_modules = {}
    advs = advs or list_advs()
    for adv in advs:
        try:
            name = core.simulate.load_adv_module(adv, in_place=target_modules)
            if conds is not None:
                adv_data = load_adv_json(name)
                if not all([cond(adv_data) for cond in conds]):
                    del target_modules[name]
            if mass is not None:
                if (mass and "mass" not in target_modules[name]) or (not mass and "mass" in target_modules[name]):
                    del target_modules[name]
        except Exception as e:
            print(f"\033[93m{0:.4f}s - load:{adv} {e}\033[0m", flush=True)
    return target_modules


def get_sim_target_modules(targets):
    target_filters = set()
    target_advs = set()
    target_kind = set()
    for target in targets:
        if target in ("all", "quick", "slow"):
            target_kind.add(target)
        elif target in ELEMENTS:
            element = str(target)
            target_filters.add(lambda d: d["c"]["ele"] == element)
        elif target in WEAPON_TYPES:
            weapontype = str(target)
            target_filters.add(lambda d: d["c"]["wt"] == weapontype)
        else:
            target_advs.add(target)
    if "quick" in target_kind:
        return get_sim_target_module_dict(target_advs, target_filters, mass=False)
    if "slow" in target_kind:
        return get_sim_target_module_dict(target_advs, target_filters, mass=True)
    return get_sim_target_module_dict(target_advs, target_filters)
    # target_modules = {}
    # if all([cmd not in targets for cmd in ('all', 'quick', 'slow')]):
    #     for adv in targets:
    #         try:
    #             core.simulate.load_adv_module(adv, in_place=target_modules)
    #         except Exception as e:
    #             print(f'\033[93m{0:.4f}s - load:{adv} {e}\033[0m', flush=True)
    #     return target_modules

    # for adv in list_advs():
    #     try:
    #         core.simulate.load_adv_module(adv, in_place=target_modules)
    #     except Exception as e:
    #         print(f'\033[93m{0:.4f}s - load:{adv} {e}\033[0m', flush=True)
    # if 'all' in targets:
    #     return target_modules
    # if 'quick' in targets:
    #     for adv, variants in target_modules.copy().items():
    #         if 'mass' in variants:
    #             del target_modules[adv]
    #     return target_modules
    # if 'slow' in targets:
    #     for adv, variants in target_modules.copy().items():
    #         if not 'mass' in variants:
    #             del target_modules[adv]
    #     return target_modules


def main(targets, do_combine, is_repair, sanity_test):
    # do_combine = False
    # is_repair = False
    # sanity_test = False
    # if '-c' in arguments:
    #     do_combine = True
    #     arguments.remove('-c')
    # if '-san' in arguments:
    #     sanity_test = True
    #     arguments.remove('-san')
    # if '-rp' in arguments:
    #     is_repair = True
    #     arguments.remove('-rp')

    target_modules = get_sim_target_modules(targets)
    if not target_modules:
        exit()

    message = []
    if is_repair:
        for advname in target_modules.keys():
            # EquipManager(advname).repair_entries()
            t_start = monotonic()
            # try:
            manager = EquipManager(advname)
            manager.repair_entries()
            print(
                "{:.4f}s - repair:{}".format(monotonic() - t_start, advname),
                flush=True,
            )
            # except Exception as e:
            #     print(
            #         f"\033[91m{monotonic()-t_start:.4f}s - repair:{advname} {e}\033[0m",
            #         flush=True,
            #     )
        return
    else:
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
        nargs="+",
        help="""targets to simulate:
    all: all advs
    quick: not mass sim advs
    slow: mass sim advs
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
