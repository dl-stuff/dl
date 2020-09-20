import os
import re
from itertools import islice
from collections import deque

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

froot = os.path.join(ROOT_DIR, 'core')
lark_file = os.path.join(froot, 'acl.lark')
with open(lark_file) as f:
    PARSER = Lark(f.read(), parser='lalr')


SHORT_CIRCUIT = {
    'AND': lambda l: bool(not l),
    'OR': lambda l: bool(l),
}


BINARY_EXPR = {
    'AND': lambda l, r: l and r,
    'OR': lambda l, r: l or r,
    'IS': lambda l, r: l is r,
    'IN': lambda l, r: l in r,
    'GT': lambda l, r: l > r,
    'LT': lambda l, r: l < r,
    'EQ': lambda l, r: l == r,
    'NE': lambda l, r: l != r,
    'GE': lambda l, r: l >= r,
    'LE': lambda l, r: l <= r,
    'ADD': lambda l, r: l + r,
    'MINUS': lambda l, r: l - r,
    'MULT': lambda l, r: l * r,
    'DIV': lambda l, r: l / r,
    'MOD': lambda l, r: l % r,
}
BINARY_EXPR['EQQ'] = BINARY_EXPR['EQ']


PIN_CMD = {
    'SEQ': lambda e: e.didx if e.dname[0] == 'x' else 0 if e.dstat == -2 else -1,
    'X': lambda e: e.didx if e.pin[0] =='x' and e.dhit == 0 else 0,
    'XF': lambda e: e.didx if e.pin[0] == 'x' else 0,
    'S': lambda e: int(e.pin[1]) if (e.pin[0] == 's' and e.pin[1].isdigit()) or e.pin[-2:] == '-x' else 0,
    'FSC': lambda e: e.pin.startswith('fs') and e.dhit == 0,
    'FSCF': lambda e: e.pin.startswith('fs'),
    'SP': lambda e: e.dname if e.pin == 'sp' else None,
    'PREP': lambda e: e.pin == 'prep',
}
PIN_CMD['CANCEL'] = lambda e: PIN_CMD['X'](e) or PIN_CMD['FSC'](e)


PARAM_EVAL = {
    'DURATION': lambda adv: adv.duration,
    'NOW': lambda _: now(),
}


LITERAL_EVAL = {
    'SIGNED_INT': int,
    'SIGNED_FLOAT': float,
    'STRING': str,
    'BOOLEAN': bool,
    'NONE': lambda: None,
}


class AclInterpreter(Interpreter):
    def bind(self, tree, acl):
        self._tree = tree
        self._acl_str = acl

    def reset(self, adv):
        self._adv = adv
        self._inst = self._adv
        self._queue = deque()

    def __call__(self, e):
        self._e = e
        self._inst = self._adv
        try:
            n_actcond = self._queue.popleft()
            if not self.visit(n_actcond):
                self._queue.appendleft(n_actcond)
        except IndexError:
            return self.visit(self._tree)

    def start(self, t):
        for child in t.children:
            result = self.visit(child)
            # log('acl', str(result), str(t))
            if result:
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
        if self.visit(t.children[0]):
            self._queue.extend(t.children[1:])
            return True
        return False

    def condition(self, t):
        args = t.children
        argl = len(t.children)
        if argl == 0:
            return True
        negate = False
        if isinstance(args[0], Token) and args[0].type == 'NOT': # NOT cond
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
            res = BINARY_EXPR[op.type](lres, rres)
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
            value = getattr(inst, last.value)
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
            return getattr(self._adv, act.value)()
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
        args = t.children[1:]
        result = getattr(self._inst, fn.value)(*map(self.visit, args))
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


FSN_PATTERN = re.compile(r'^`?(fs|s)(\d+)(\(([^)]+)\))?')
def _pre_parse(acl):
    return '\n'.join(filter(None,(
        FSN_PATTERN.sub(r'`\1(\2,\4)', l.strip())
        for l in acl.split('\n')
    )))


def build_acl(acl):
    acl = _pre_parse(acl)
    tree = PARSER.parse(acl)
    interpreter = AclInterpreter()
    interpreter.bind(tree, acl)
    return interpreter

