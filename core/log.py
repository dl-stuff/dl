import sys
import re
from collections import defaultdict
import core.timeline

DACT_NAME = re.compile(r"(?:ds\d+(?:_[A-Za-z0-9]+)?|dfs\d*(?:_[A-Za-z0-9]+)?|dx(\d)+(?:_[A-Za-z0-9]+)?)")


class Log:
    DEBUG = False

    def __init__(self):
        self.reset()

    def reset(self):
        self.record = []
        self.damage = {"x": {}, "s": {}, "f": {}, "d": {}, "o": {}}
        self.counts = {"x": {}, "s": {}, "f": {}, "d": {}, "o": {}}
        self.heal = {}
        self.datasets = defaultdict(dict)
        self.p_buff = None
        self.team_buff = 0
        self.team_doublebuffs = 0
        self.team_amp_publish = {}
        self.team_tension = {}
        self.act_seq = []
        self.hitattr_set = set()
        self.total_hits = 0

        self.shift_name = None
        self.shift_dmg = None
        self.shift_acts = []
        self.shift_start = 0
        self.shift_count = 0

    def convert_dataset(self):
        if "doublebuff" in self.datasets:
            converted_doublebuff = {}
            stacks = 0
            for t, v in sorted(self.datasets["doublebuff"].items()):
                stacks += v
                converted_doublebuff[t] = stacks
            self.datasets["doublebuff"] = converted_doublebuff
        return {cat: [{"x": t, "y": d} for t, d in sorted(data.items())] for cat, data in self.datasets.items()}

    @staticmethod
    def update_dict(dict, name: str, value, replace=False):
        # if fullname:
        if replace:
            dict[name] = value
        else:
            try:
                dict[name] += value
            except KeyError:
                dict[name] = value

    @staticmethod
    def fmt_hitattr_v(v):
        if isinstance(v, list):
            return "[" + ",".join(map(str, v)) + "]"
        if isinstance(v, dict):
            return Log.fmt_hitattr(v)
        return str(v)

    @staticmethod
    def fmt_hitattr(attr):
        return "{" + "/".join([f"{k}:{Log.fmt_hitattr_v(v)}" for k, v in attr.items()]) + "}"

    def set_log_shift(self, shift_name=None, end_reason=None):
        if shift_name and not self.shift_name:
            self.shift_name = shift_name
            self.shift_dmg = 0
            self.shift_acts = []
            self.shift_start = core.timeline.now()
            self.shift_count += 1
        elif self.shift_name and end_reason:
            duration = core.timeline.now() - self.shift_start
            for i, name in enumerate(self.shift_acts):
                if isinstance(name, int):
                    self.shift_acts[i] = f"c{self.shift_acts[i]}"
            shift_act_str = " ".join(self.shift_acts)
            self.log(
                "dshift_end",
                f"{self.shift_dmg:.1f}/{duration:.1f}s",
                f"{self.shift_dmg / duration:.2f} dps",
                shift_act_str,
                end_reason,
            )
            if not shift_act_str:
                self.act_seq.append(f"drg")
            else:
                self.act_seq.append(f"drg:{shift_act_str}")
            self.shift_name = None

    def log_shift_data(self, category, name, args):
        try:
            res = DACT_NAME.match(name)
            if not res:
                return
        except TypeError:
            return
        if category == "cast":
            self.shift_acts.append(name.strip("d"))
        elif category == "x":
            xn = int(res.group(1))
            if not self.shift_acts or self.shift_acts[-1] != xn - 1:
                self.shift_acts.append(xn)
            else:
                self.shift_acts[-1] = xn
        elif category == "dmg":
            self.shift_dmg += float(args[2])

    def log_hitattr(self, name, attr):
        attr_str = Log.fmt_hitattr(attr)
        if (name, attr_str) in self.hitattr_set:
            return
        self.hitattr_set.add((name, attr_str))
        log("hitattr", name, attr_str)
        return attr_str

    def log(self, *args):
        time_now = core.timeline.now()
        n_rec = [time_now, *args]
        if len(args) >= 2:
            category = args[0]
            name = args[1]

            if self.shift_name:
                self.log_shift_data(category, name, args)

            if category == "dmg":
                dmg_amount = float(args[2])
                if name[0:2] == "o_" and name[2] in self.damage:
                    name = name[2:]
                if name[0] in self.damage:
                    self.update_dict(self.damage[name[0]], name, dmg_amount)
                else:
                    if name[0] == "#":
                        name = name[1:]
                        n_rec[2] = name
                    self.update_dict(self.damage["o"], name, dmg_amount)
                self.update_dict(self.datasets["dmg"], time_now, dmg_amount)

            elif category == "x" or category == "cast":
                if name[0] == "#":
                    name = name[1:]
                    n_rec[2] = name
                    self.update_dict(self.counts["o"], name, 1)
                else:
                    self.update_dict(self.counts[name[0]], name, 1)
                # name1 = name.split('_')[0]
                # if name1 != name:
                #     self.update_dict(self.counts[name[0]], name1, 1)
                if not self.shift_name:
                    self.act_seq.append(name)

            elif category == "buff" and name == "team":
                buff_amount = float(args[2])
                if self.p_buff is not None:
                    pt, pb = self.p_buff
                    self.team_buff += (time_now - pt) * pb
                self.p_buff = (time_now, buff_amount)
                self.update_dict(self.datasets["team"], time_now, buff_amount, replace=True)

            elif category == "buff" and name == "doublebuff":
                self.team_doublebuffs += 1
                self.update_dict(self.datasets["doublebuff"], time_now, 1)
                self.update_dict(self.datasets["doublebuff"], time_now + float(args[2]), -1)

            elif category in ("energy", "inspiration") and name == "team":
                self.update_dict(self.team_tension, category, float(args[2]))

            elif category == "affliction":
                self.update_dict(self.datasets[name], time_now, float(args[2]) * 100)

            elif category == "heal":
                heal_value = float(args[2])
                self.update_dict(self.heal, args[3], heal_value)
                self.update_dict(self.datasets[f"heal_{args[3]}"], time_now, heal_value)

            elif category == "amp" and args[-1]:
                try:
                    self.team_amp_publish[args[1]].append(time_now)
                except KeyError:
                    self.team_amp_publish[args[1]] = [time_now]
        if self.DEBUG:
            self.write_log_entry(n_rec, sys.stdout, flush=True)
        self.record.append(n_rec)

    def filter_iter(self, log_filter):
        for entry in self.record:
            try:
                if entry[1] in log_filter:
                    yield entry
            except:
                continue

    def write_log_entry(self, entry, output, flush=False):
        time = entry[0]
        output.write("{:>8.3f}: ".format(time))
        for value in entry[1:]:
            if isinstance(value, float):
                output.write("{:<16.3f},".format(value))
            else:
                try:
                    output.write("{:<16},".format(str(value)))
                except TypeError:
                    raise TypeError(str(entry))
        output.write("\n")
        if flush:
            output.flush()

    def write_logs(self, log_filter=None, output=None, maxlen=None):
        if output is None:
            output = sys.stdout
        if log_filter is None:
            log_iter = self.record
        else:
            log_iter = self.filter_iter(log_filter)
        maxlen = maxlen or -1
        for entry in log_iter:
            self.write_log_entry(entry, output)
            maxlen -= 1
            if maxlen == 0:
                output.write("......")
                return

    def get_log_list(self):
        return self.record


loglevel = 0

g_logs = Log()
log = g_logs.log
logcat = g_logs.write_logs
logget = g_logs.get_log_list
logreset = g_logs.reset
