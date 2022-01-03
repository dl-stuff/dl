import io
import itertools
import json
from conf import ELEMENTS, get_fullname
import traceback
import subprocess

from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS

import core.simulate
from core.afflic import AFFLICTION_LIST, Afflics
from conf import (
    ROOT_DIR,
    TRIBE_TYPES,
    SKIP_VARIANT,
    skillshare,
    wyrmprints,
    weapons,
    mono_elecoabs,
    load_adv_by_element,
    load_drg_by_element,
)
from conf.equip import (
    AfflictionCondition,
    MonoCondition,
    SituationCondition,
    build_equip_condition,
    get_equip_manager,
)

app = Flask(__name__)
CORS(app)


# Helpers
SIMULATED_BUFFS = {
    "str_buff": (-100, 200, 100),
    "def_down": (-50, 200, 100),
    "critr": (-100, 100, 100),
    "critd": (-100, 200, 100),
    "doublebuff_interval": (0.5, 600.0, 1),
    "count": (0, float("inf"), 1),
    "echo": (0, float("inf"), 1),
    "dprep": (0, 100, 1),
}
RARITY_MAP = {1: "formA", 2: "formB", 3: "formC"}


ADVS_BY_ELEMENT = {ele: load_adv_by_element(ele) for ele in ELEMENTS}
DRAGONS_BY_ELEMENT = {ele: load_drg_by_element(ele) for ele in ELEMENTS}


ADV_MODULES = {}
for fn in itertools.chain(ADVS_BY_ELEMENT.values()):
    core.simulate.load_adv_module(fn, in_place=ADV_MODULES)


def set_teamdps_res(result, logs, real_d, suffix=""):
    result["extra" + suffix] = {}
    if logs.team_buff > 0:
        result["extra" + suffix]["team_buff"] = "+{}%".format(round(logs.team_buff / real_d * 100))
    for tension, count in logs.team_tension.items():
        if count > 0:
            result["extra" + suffix]["team_{}".format(tension)] = "{} stacks".format(round(count))
    return result


def run_adv_test(advname, variant, wp=None, dra=None, wep=None, acl=None, dacl=None, conf=None, t=180, log=5, mass=0):
    advmodule = ADV_MODULES[advname][variant]

    if conf is None:
        conf = {}

    conf["flask_env"] = True
    if wp is not None:
        conf["slots.a"] = list(wp)
    if dra is not None:
        conf["slots.d"] = dra
    if wep is not None:
        conf["slots.w"] = wep
    if acl:
        conf["acl"] = acl
    conf["dacl"] = dacl

    result = {}

    try:
        adv, real_d, report = core.simulate.test(advname, advmodule, conf, t, log, mass, output=None)
        result["test_output"] = report
    except Exception as e:
        result["error"] = traceback.format_exc(limit=-1)
        return result

    if variant not in SKIP_VARIANT:
        adv.equip_manager.accept_new_entry(adv, real_d)

    result["logs"] = {}
    fn = io.StringIO()
    adv.logs.write_logs(output=fn, log_filter=["dshift", "dragondrive"])
    result["logs"]["dragon"] = fn.getvalue()
    fn = io.StringIO()
    core.simulate.act_sum(adv.logs.act_seq, fn)
    result["logs"]["action"] = fn.getvalue()
    misc_data = [f"Hitcount - {adv.logs.total_hits} ({adv.logs.total_hits/real_d:.2f}/s)"]
    if adv.logs.heal:
        misc_data.append("Healing - " + ", ".join(["{}: {:.0f}".format(k, v) for k, v in adv.logs.heal.items() if v]))
    result["logs"]["misc"] = "\n".join(misc_data)
    result["logs"]["summation"] = "\n".join(["{}: {}".format(k, v) for k, v in adv.logs.counts.items() if v])
    fn = io.StringIO()
    adv.logs.write_logs(output=fn, maxlen=3000)
    result["logs"]["timeline"] = fn.getvalue()

    result["chart"] = {}
    result["chart"] = adv.logs.convert_dataset()

    return result


# API
@app.route("/simc_adv_test", methods=["POST"])
def simc_adv_test():
    if not request.method == "POST":
        return "Wrong request method."
    params = request.get_json(silent=True)
    advname = "Patia" if not "adv" in params or params["adv"] is None else params["adv"]
    variant = params.get("variant")
    wp = params.get("wp")
    dra = params.get("dra")
    wep = params.get("wep")
    acl = params.get("acl")
    dacl = params.get("dacl")
    t = 180 if not "t" in params else min(abs(float(params["t"])), 600.0)
    log = 5
    mass = 0
    coab = params.get("coab")
    share = params.get("share")
    # latency = 0 if 'latency' not in params else abs(float(params['latency']))
    # print(params, flush=True)

    conf = {}
    if "missile" in params:
        missile = abs(float(params["missile"]))
        if missile > 0:
            conf["missile_iv"] = missile
    if "hp" in params:
        conf["hp"] = min(abs(int(params["hp"])), 100)
    if "specialmode" in params:
        if params["specialmode"].startswith("berserk"):
            conf["berserk"] = float(params["specialmode"].replace("berserk", ""))
        else:
            conf[params["specialmode"]] = True
    if "classbane" in params and (params["classbane"] in TRIBE_TYPES or params["classbane"] == "HDT"):
        conf["classbane"] = params["classbane"]
    if "dumb" in params:
        conf["dumb"] = params["dumb"]
    if "fleet" in params:
        conf["fleet"] = min(3, abs(params["fleet"]))
    if coab is not None:
        conf["coabs"] = coab
    if share is not None:
        conf["share"] = share
    for afflic in AFFLICTION_LIST:
        try:
            conf[f"sim_afflict.{afflic}"] = min(abs(int(params["sim_afflict"][afflic])), 100) / 100
        except KeyError:
            pass
        try:
            conf[f"afflict_res.{afflic}"] = min(abs(int(params["afflict_res"][afflic])), 999)
        except KeyError:
            pass

    for buff, bounds in SIMULATED_BUFFS.items():
        b_min, b_max, b_ratio = bounds
        try:
            conf[f"sim_buffbot.{buff}"] = min(max(float(params["sim_buff"][buff]), b_min), b_max) / b_ratio
        except KeyError:
            pass

    result = run_adv_test(
        advname,
        variant,
        wp=wp,
        dra=dra,
        wep=wep,
        acl=acl,
        dacl=dacl,
        conf=conf,
        t=t,
        log=log,
        mass=mass,
    )
    return jsonify(result)


def summarize_coab(coab):
    if not coab["chain"]:
        return (coab["category"].lower(), None)
    return (coab["category"].lower(), "|".join(map(str, coab["chain"][0])))


@app.route("/simc_adv_slotlist", methods=["POST"])
def get_adv_slotlist():
    if not request.method == "POST":
        return "Wrong request method."
    result = {}
    result["adv"] = {}
    params = request.get_json(silent=True)
    advname = params.get("adv", None)
    variant = params.get("variant", None)
    equip_cond, opt_mode = build_equip_condition(params.get("equip", None))
    duration = params.get("t", 180)
    duration = max(min(((int(duration) // 60) * 60), 180), 60)
    if advname is not None:
        adv = ADV_MODULES[advname][variant](name=advname, duration=duration, equip_conditions=equip_cond, opt_mode=opt_mode)
        adv.config_slots()
        adv.doconfig()
        result["adv"]["basename"] = adv.name
        result["adv"]["ele"] = adv.slots.c.ele
        result["adv"]["wt"] = adv.slots.c.wt
        result["adv"]["pref_dra"] = adv.slots.d.qual
        result["adv"]["pref_wep"] = adv.slots.w.series
        result["adv"]["pref_wp"] = adv.slots.a.qual_lst
        result["adv"]["pref_coab"] = adv.conf["coabs"] or []
        result["adv"]["pref_share"] = adv.conf["share"] or []
        adv.slots.d.oninit(adv)
        adv.config_acl()
        result["adv"]["acl"] = adv.conf.acl
        if adv.DISABLE_DACL:
            result["adv"]["dacl"] = "DISABLED"
        else:
            result["adv"]["dacl"] = adv.conf.dacl
        if opt_mode is not None and adv.equip_manager[equip_cond] != opt_mode:
            tdps = adv.equip_manager[equip_cond].tdps
            if tdps and 0 <= tdps <= 200000:
                result["adv"]["tdps"] = tdps

        available_wpn = {
            **weapons[adv.slots.c.wt]["any"],
            **weapons[adv.slots.c.wt][adv.slots.c.ele],
        }
        result["weapons"] = {}
        for series, wpn in sorted(available_wpn.items(), key=lambda w: -w[1]["w"]["att"]):
            result["weapons"][series] = f'{wpn["w"]["series"]} | {wpn["w"]["name"]}'
        result["dragons"] = DRAGONS_BY_ELEMENT[adv.slots.c.ele]
        # gold fafu lul
        result["dragons"]["Gold_Fafnir"] = "Gold Fafnir"

        if equip_cond.mono == MonoCondition.MONO:
            result["coabilities"] = {k: (get_fullname(k), *summarize_coab(v)) for k, v in mono_elecoabs[adv.slots.c.ele].items()}
        else:
            result["coabilities"] = {k: (get_fullname(k), *summarize_coab(v)) for k, v in adv.slots.c.valid_coabs.items()}

        result["ui"] = {}
        if equip_cond.aff == AfflictionCondition.IMMUNE:
            result["ui"]["afflict_res"] = Afflics.RESIST_PROFILES["immune"]
        else:
            result["ui"]["afflict_res"] = Afflics.RESIST_PROFILES[(adv.slots.c.ele, equip_cond.sit == SituationCondition.NIHILISM)]
        if equip_cond.aff == AfflictionCondition.ALWAYS:
            result["ui"]["sim_afflict"] = {aff: 100 for aff in adv.sim_afflict}
        else:
            result["ui"]["sim_afflict"] = {aff: "" for aff in AFFLICTION_LIST}
        if equip_cond.sit == SituationCondition.NIHILISM:
            result["ui"]["specialmode"] = "nihilism"
        else:
            result["ui"]["specialmode"] = "none"
        result["ui"]["aff"] = str(equip_cond.aff)
        result["ui"]["sit"] = str(equip_cond.sit)
        if opt_mode is None:
            result["ui"]["opt"] = str(adv.equip_manager[equip_cond].pref)
        else:
            result["ui"]["opt"] = str(opt_mode)
    return jsonify(result)


@app.route("/simc_adv_wp_list", methods=["GET", "POST"])
def get_adv_wp_list():
    if not (request.method == "GET" or request.method == "POST"):
        return "Wrong request method."
    result = {}
    result["adv"] = {}
    for name, variants in ADV_MODULES.items():
        result["adv"][name] = {
            "fullname": get_fullname(name),
            "variants": [vkey for vkey in variants.keys() if vkey is not None and vkey != "mass"],
        }
    wplists = {"formA": {}, "formB": {}, "formC": {}}
    for wp, data in wyrmprints.items():
        ab_str = f'-{data["union"]}'
        if data["a"]:
            ab_str = "[" + "‖".join(["|".join(map(str, ab)) for ab in data["a"]]) + "]" + ab_str
        else:
            ab_str = "[]" + ab_str
        display_name = data["name"] + " " + ab_str
        wplists[RARITY_MAP[data["rarity"]]][wp] = display_name
    result["wyrmprints"] = wplists
    result["skillshare"] = {k: {"fullname": get_fullname(k), **v} for k, v in skillshare.items()}
    return jsonify(result)


@app.route("/simc_adv_equip", methods=["GET"])
def get_adv_equip():
    equip_manager = get_equip_manager(request.args.get("adv", default=None), request.args.get("variant", default=None))
    return "<pre>" + equip_manager.display_json().replace(">", "&gt;").replace("<", "&lt;") + "</pre>"


@app.route("/simc_git_diff", methods=["GET"])
def get_git_diff():
    return "<pre>" + subprocess.check_output(["git", "diff", "conf/equip"], cwd=ROOT_DIR, encoding="UTF-8").replace(">", "&gt;").replace("<", "&lt;") + "</pre>"
