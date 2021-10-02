import os
import re
from itertools import islice
from collections import deque

from lark.exceptions import UnexpectedToken

from core.log import log

CHAR_LIMIT = 1000
CONTINUE = "<continue>"


def pairs(iterator):
    "s -> (s0,s1), (s2,s3), (s4, s5), ..."
    a = islice(iterator, 0, None, 2)
    b = islice(iterator, 1, None, 2)
    return zip(a, b)


from lark import Lark, Tree, Token
from lark.visitors import Visitor, Interpreter, v_args

from core.timeline import now
from core.log import log
from conf import ROOT_DIR

froot = os.path.join(ROOT_DIR, "core")
lark_file = os.path.join(froot, "acl.lark")
with open(lark_file) as f:
    PARSER = Lark(f.read(), parser="lalr", maybe_placeholders=True)


SHORT_CIRCUIT = {
    "AND": lambda l: bool(not l),
    "OR": lambda l: bool(l),
}


BINARY_EXPR = {
    "AND": lambda l, r: l and r,
    "OR": lambda l, r: l or r,
    "IS": lambda l, r: l is r,
    "IN": lambda l, r: l in r,
    "GT": lambda l, r: l > r,
    "LT": lambda l, r: l < r,
    "EQ": lambda l, r: l == r,
    "NE": lambda l, r: l != r,
    "GE": lambda l, r: l >= r,
    "LE": lambda l, r: l <= r,
    "ADD": lambda l, r: l + r,
    "MINUS": lambda l, r: l - r,
    "MULT": lambda l, r: l * r,
    "DIV": lambda l, r: l / r,
    "MOD": lambda l, r: l % r,
}
BINARY_EXPR["EQQ"] = BINARY_EXPR["EQ"]
BINARY_EXPR_TOKENS = {
    "GT": ">",
    "LT": "<",
    "EQ": "=",
    "NE": "!=",
    "GE": ">=",
    "LE": "<=",
    "ADD": "+",
    "MINUS": "-",
    "MULT": "*",
    "DIV": "/",
    "MOD": "%",
}


S_PATTERN = re.compile(r"d?s(\d+)-?x?")


def _pin_s(e):
    if res := S_PATTERN.match(e.pin):
        return int(res.group(1))
    return 0


PIN_CMD = {
    "SEQ": lambda e: e.didx if e.dname[0] == "x" else 0 if e.dstat == -2 else -1,
    "X": lambda e: e.didx if e.pin[0] == "x" and e.dstat != -1 and e.dhit == 0 else 0,
    "XF": lambda e: e.didx if e.pin[0] == "x" and e.dstat != -1 else 0,
    "S": _pin_s,
    "FSC": lambda e: e.pin.startswith("fs") and e.dstat != -1 and e.dhit == 0,
    "FSCF": lambda e: e.pin.startswith("fs") and e.dstat != -1,
    "SP": lambda e: e.dname if e.pin == "sp" else None,
    "PREP": lambda e: e.pin == "prep",
    "REPEAT": lambda e: e.didx if e.dname.endswith("repeat") else 0,
}
PIN_CMD["CANCEL"] = lambda e: PIN_CMD["X"](e) or PIN_CMD["FSC"](e)


PARAM_EVAL = {
    "DURATION": lambda adv: adv.duration,
    "NOW": lambda _: now(),
}


LITERAL_EVAL = {
    "SIGNED_INT": int,
    "SIGNED_FLOAT": float,
    "STRING": str,
    "BOOLEAN": bool,
    "NONE": lambda: None,
}


def allow_acl(f):
    f.allow_acl = True
    return f


def check_allow_acl(f):
    # res = getattr(f, 'allow_acl', False)
    # if not res:
    #     raise RuntimeError(str(f))
    # return res
    return getattr(f, "allow_acl", False)


class AclInterpreter(Interpreter):
    def bind(self, tree, acl):
        self._tree = tree
        self._acl_str = acl

    def reset(self, adv):
        self._adv = adv
        self._inst = self._adv
        self._queue = deque()
        self._queue_while = None

    def checkqueue(self):
        if self._queue_while is not None and not self.visit(self._queue_while):
            self._queue.clear()
            self._queue_while = None
            return False
        try:
            n_actcond = self._queue.popleft()
            if not self.visit(n_actcond):
                self._queue.appendleft(n_actcond)
            return True
        except IndexError:
            pass
        return False

    def __call__(self, e):
        self._e = e
        self._inst = self._adv
        if self.checkqueue():
            return False
        return self.visit(self._tree)

    def visit(self, t):
        result = super().visit(t)
        if t.data in ("literal", "selfcond", "pincond"):
            t._visited = True
        else:
            t._visited = bool(result) or getattr(t, "_visited", False)
        # if t.data == "action":
        #     log("visited", str(result), str(t))
        return result

    def start(self, t):
        for child in t.children:
            result = self.visit(child)
            # log("acl", str(result), str(child))
            if result and result is not CONTINUE:
                return True
        return False

    def ifelse(self, t):
        else_block = None
        if len(t.children) % 2 > 0:
            else_block = t.children[-1]
            children_iter = pairs(t.children[:-1])
        else:
            children_iter = pairs(t.children)
        for condition, block in children_iter:
            if self.visit(condition):
                return self.visit(block)
        if else_block is not None:
            return self.visit(else_block)
        return False

    def ifqueue(self, t):
        if self._queue:
            return False
        if t.children[0] is None or self.visit(t.children[0]):
            self._queue_while = t.children[1]
            self._queue.extend(t.children[2:])
            return self.checkqueue()
        return False

    def condition(self, t):
        args = t.children
        argl = len(t.children)
        if argl == 0:
            return True
        negate = False
        if isinstance(args[0], Token) and args[0].type == "NOT":  # NOT cond
            args = args[1:]
            argl -= 1
            negate = True
        if argl == 1:
            res = self.visit(args[0])
        else:
            left, op, right = args
            lres = self.visit(left)
            try:
                if SHORT_CIRCUIT[op.type](lres):
                    return not lres if negate else lres
            except KeyError:
                pass
            rres = self.visit(right)
            try:
                res = BINARY_EXPR[op.type](lres, rres)
            except TypeError:
                # assume true when type error
                res = not negate
        return not res if negate else res

    def selfcond(self, t):
        inst = self._adv
        children = t.children[0:-1]
        last = t.children[-1]
        for child in children:
            inst = getattr(inst, child.value)
        try:
            self._inst = inst
            value = self.visit(last)
            self._inst = self._adv
        except AttributeError:
            value = getattr(inst, last.value, None)
        return value

    def arithmetic(self, t):
        if len(t.children) == 3:
            left, op, right = t.children
            res = BINARY_EXPR[op.type](self.visit(left), self.visit(right))
            return res
        return 0

    # @v_args(inline=True)
    # def actcond(self, action, condition):
    def actcond(self, t):
        action, condition = t.children
        if self.visit(condition):
            return self.visit(action)
        return False

    # @v_args(inline=True)
    # def params(self, p):
    def params(self, t):
        p = t.children[0]
        return PARAM_EVAL[p.type](self._adv)

    # @v_args(inline=True)
    # def pincond(self, cmd):
    def pincond(self, t):
        cmd = t.children[0]
        return PIN_CMD[cmd.type](self._e)

    # @v_args(inline=True)
    # def action(self, act):
    def action(self, t):
        act = t.children[0]
        self._inst = self._adv
        if isinstance(act, Token):
            act_obj = getattr(self._inst, act.value)
            if not check_allow_acl(act_obj):
                return False
            return act_obj()
        else:
            return self.visit(act)

    # @v_args(inline=True)
    # def literal(self, token):
    def literal(self, t):
        token = t.children[0]
        return LITERAL_EVAL[token.type](token.value)

    # @v_args(inline=True)
    # def function(self, fn, *args):
    def function(self, t):
        fn = t.children[0]
        fn_obj = getattr(self._inst, fn.value)
        if not check_allow_acl(fn_obj):
            return False
        args = t.children[1:]
        result = fn_obj(*map(self.visit, args))
        # log('acl', str(t), str(result))
        return result

    # @v_args(inline=True)
    # def indice(self, fn, idx):
    def indice(self, t):
        fn, idx = t.children
        if isinstance(fn, Token):
            return getattr(self._inst, fn.value)[self.visit(idx)]
        else:
            return self.visit(fn)[self.visit(idx)]


def remove_paranthesis(condres):
    if condres[0] == "(" and condres[-1] == ")":
        return condres[1:-1]
    return condres


class AclRegenerator(Interpreter):
    CTRL = ("if", "elif", "else", "queue", "end")

    def visit(self, t):
        if getattr(t, "_visited", False):
            return super().visit(t)
        return False

    def start(self, t):
        childres = []
        for child in t.children:
            result = self.visit(child)
            if not result:
                continue
            if isinstance(result, str):
                if not result.startswith("`") and not any((result.startswith(ctrl) for ctrl in AclRegenerator.CTRL)):
                    result = f"`{result}"
                childres.append(result)
            elif isinstance(result, list):
                result = (f"`{res}" if not res.startswith("`") and not any((res.startswith(ctrl) for ctrl in AclRegenerator.CTRL)) else res for res in result)
                childres.extend(result)
        return "\n".join(childres)

    def ifelse(self, t):
        if_else_list = []
        else_block = None
        if len(t.children) % 2 > 0:
            else_block = t.children[-1]
            children_iter = pairs(t.children[:-1])
        else:
            children_iter = pairs(t.children)
        for idx, condblock in enumerate(children_iter):
            condition, block = condblock
            condres = self.visit(condition)
            if condres:
                condres = remove_paranthesis(condres)
                if idx == 0:
                    if_else_list.append(f"if {condres}")
                else:
                    if_else_list.append(f"elif {condres}")
                blockres = self.visit(block)
                if blockres:
                    if_else_list.append(self.visit(block))
        if else_block is not None:
            elseres = self.visit(else_block)
            if elseres:
                if not if_else_list:
                    return self.visit(else_block)
                if_else_list.append("else")
                if_else_list.append(self.visit(else_block))
        if if_else_list:
            if_else_list.append("end")
            if_else_list = (f"`{res}" if not res.startswith("`") and not any((res.startswith(ctrl) for ctrl in AclRegenerator.CTRL)) else res for res in if_else_list)
            return "\n".join(if_else_list)
        return False

    def ifqueue(self, t):
        queue_start = "queue"
        had_ran = True
        if t.children[0] is not None:
            condres = self.visit(t.children[0])
            if condres:
                queue_start += " " + remove_paranthesis(condres)
            had_ran = bool(condres)
        if t.children[1] is not None:
            queue_start += " while " + self.visit(t.children[1])
        if had_ran:
            queue_list = []
            for child in t.children[2:]:
                queue_child_res = self.visit(child)
                if queue_child_res:
                    queue_list.append(queue_child_res)
            return f"{queue_start}\n`" + ";".join(queue_list) + "\nend"
        return False

    def condition(self, t):
        args = t.children
        argl = len(t.children)
        if argl == 0:
            return None
        condstr = []
        negate = False
        combined = None
        if isinstance(args[0], Token) and args[0].type == "NOT":  # NOT cond
            args = args[1:]
            argl -= 1
            negate = True
        if argl == 1:
            arglres = self.visit(args[0])
            if arglres:
                condstr.append(arglres)
        else:
            left, op, right = args
            lres = self.visit(left)
            if lres:
                condstr.append(lres)
            rres = self.visit(right)
            if rres:
                try:
                    if lres:
                        combined = f"{lres}{BINARY_EXPR_TOKENS[op.type]}{rres}"
                        condstr[-1] = combined
                except KeyError:
                    if lres:
                        condstr.append(op.type.lower())
                    condstr.append(rres)
        if condstr:
            if negate:
                condstr.insert(0, "not")
            if negate or combined:
                return " ".join(condstr)
            return "(" + " ".join(condstr) + ")"
        return False

    def selfcond(self, t):
        children = t.children[:-1]
        last = t.children[-1]
        childlist = [str(child.value) for child in children]
        if isinstance(last, Token):
            childlist.append(str(last.value))
        else:
            lastres = self.visit(last)
            if not lastres:
                return False
            childlist.append(lastres)
        return ".".join(childlist)

    def arithmetic(self, t):
        if len(t.children) == 3:
            left, op, right = t.children
            return f"({self.visit(left)}{BINARY_EXPR_TOKENS[op.type]}{self.visit(right)})"
        return False

    def actcond(self, t):
        action, condition = t.children
        condres = self.visit(condition)
        if condres:
            actionres = self.visit(action)
            condres = remove_paranthesis(condres)
            if actionres:
                return f"{actionres}, {condres}"

    def params(self, t):
        p = t.children[0]
        return p.type.lower()

    def pincond(self, t):
        cmd = t.children[0]
        return cmd.type.lower()

    def action(self, t):
        act = t.children[0]
        if isinstance(act, Token):
            return act.value
        else:
            return self.visit(act)

    def literal(self, t):
        token = t.children[0]
        if token.type == "STRING":
            return f"'{token.value}'"
        return str(LITERAL_EVAL[token.type](token.value))

    def function(self, t):
        fn = t.children[0]
        args = t.children[1:]
        if XSF.match(fn.value):
            if len(args) == 0:
                return str(fn.value)
            elif len(args) == 1:
                return f"{fn.value}{self.visit(args[0])}"
            else:
                argstr = ", ".join((str(self.visit(arg)).strip("'") for arg in args[1:]))
                return f"{fn.value}{self.visit(args[0])}({argstr})"
        argstr = ", ".join((str(self.visit(arg)).strip("'") for arg in args))
        return f"{fn.value}({argstr})"

    def indice(self, t):
        fn, idx = t.children
        visited_idx = self.visit(idx).strip("'")
        if isinstance(fn, Token):
            return f"{fn.value}[{visited_idx}]"
        else:
            fnres = self.visit(fn)
            if fnres:
                return f"{fnres}[{visited_idx}]"


XSF = re.compile(r"d?(fs|s|x)")
SEP_PATTERN = re.compile(r"(^|;|\n)")
XSF_PATTERN = re.compile(r"^`?(d?(fs|s)|x|dx)(\d+)(\(([^)]+)\))?")
DRG_PATTERN = re.compile(r"^(.*)dragon\s*\(([A-Za-z0-9\-]+)\)(.*)")


def _pre_parse(acl):
    pre_parsed = []

    in_queue = False
    join_latest_2 = False
    for line in SEP_PATTERN.split(acl):
        line = line.strip()
        if not line:
            continue
        if line == ";":
            join_latest_2 = True
            continue
        if line == "end":
            in_queue = False
        elif line.startswith("queue"):
            in_queue = True
        drgres = DRG_PATTERN.match(line)
        if drgres:
            # dragon actstr -> acl shim
            str_b4, dact_str, str_af = drgres.groups()
            str_b4 = str_b4.strip("` ")
            queue_str = []
            last_dx = None
            for a in dact_str.split("-"):
                if a in ("s", "ds"):
                    if last_dx is not None:
                        queue_str[-1] = "ds(1),x={}".format(last_dx)
                    else:
                        queue_str.append("ds(1),cancel")
                    continue
                last_dx = None
                if a in ("sf", "dsf"):
                    queue_str.append("ds(1)")
                elif a in ("fs", "dfs"):
                    queue_str.append("fs")
                elif a[0] == "c":
                    last_dx = a[1:]
                    queue_str.append("dx({})".format(a[1:]))
                elif a == "dodge":
                    queue_str.append("dodge")
                elif a == "end":
                    queue_str.append("sack")
            if in_queue:
                join_latest_2 = True
                line = "dragon{};{}".format(str_af, ";".join(queue_str))
            else:
                line = "`dragon{}\nqueue while in_dform\n`{};\nend".format(str_af, ";".join(queue_str))
        else:
            # s1 -> s(1,)
            line = XSF_PATTERN.sub(r"`\1(\3,\5)", line.strip())

        if join_latest_2:
            pre_parsed[-1] += ";" + line
            join_latest_2 = False
        else:
            pre_parsed.append(line)

    return "\n".join(pre_parsed)


def build_acl(acl):
    if isinstance(acl, list):
        acl = "\n".join(acl)
    if len(acl) > CHAR_LIMIT:
        raise ValueError(f"ACL cannot be longer than {CHAR_LIMIT} characters.")
    acl = _pre_parse(acl)
    tree = PARSER.parse(acl)
    interpreter = AclInterpreter()
    interpreter.bind(tree, acl)
    return interpreter


REGENERATOR = AclRegenerator()


def regenerate_acl(interpreter):
    acl_str = REGENERATOR.visit(interpreter._tree) or ""
    if isinstance(acl_str, list):
        acl_str = "\n".join(acl_str)
    comments = "\n".join((line.strip() for line in interpreter._acl_str.split("\n") if line.strip().startswith("#")))
    if comments:
        # no real way to tell where comments were relatively
        # perhaps incl into parse tree?
        acl_str = f"{comments}\n{acl_str}"
    return acl_str
