import os
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


lark_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'acl.lark')
with open(lark_file) as f:
    PARSER = Lark(f.read())


BINARY_EXPR = {
    'AND': lambda l, r: l and r,
    'OR': lambda l, r: l or r,
    'IS': lambda l, r: l is r,
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


PIN_CMD = {
    'SEQ': lambda e: e.didx if e.dname[0] == 'x' else 0 if e.dstat == -2 else -1,
    'X': lambda e: e.didx if e.pin =='x' else 0,
    'S': lambda e: int(e.pin[1]) if (e.pin[0] == 's' and e.pin[1].isdigit()) or e.pin[-2:] == '-x' else 0,
    'FSC': lambda e: e.pin == 'fs',
    'CANCEL': lambda e: e.pin =='x' or e.pin == 'fs',
    'SP': lambda e: e.dname if e.pin == 'sp' else None,
    'PREP': lambda e: e.pin == 'prep',
}


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
    def bind(self, acl, adv):
        self._acl = acl
        self._adv = adv
        self._inst = self._adv
        self._queue = deque()
        
    def run(self, e):
        self._e = e
        try:
            n_actcond = self._queue.popleft()
            if not self.visit(n_actcond):
                self._queue.appendleft(n_actcond)
        except IndexError:
            return self.visit(self._acl)

    def block(self, t):
        for child in t.children:
            if self.visit(child):
                return True
        return False

    def ifelse(self, t):
        for condition, block in pairs(t.children):
            if self.visit(condition):
                return self.visit(block)
        return False

    def ifqueue(self, t):
        if self.visit(t.children[0]):
            self._queue.extend(t.children[1:])
            return True
        return False

    def condition(self, t):
        argl = len(t.children)
        if argl == 0:
            return True
        if argl == 1:
            res = self.visit(t.children[0])
        elif argl == 2 and t.children[0].type == 'NOT': # NOT cond
            res = not self.visit(t.children[1])
        elif argl == 3:
            left, op, right = t.children
            res = BINARY_EXPR[op.type](self.visit(left), self.visit(right))
        return res

    def selfcond(self, t):
        inst = self._adv
        for child in t.children[:-1]:
            inst = getattr(inst, child.value)
        last = t.children[-1]
        try:
            self._inst = inst
            value = self.visit(last)
            self._inst = self._adv
        except AttributeError:
            value = getattr(inst, last.value)
        return value

    @v_args(inline=True)
    def actcond(self, action, condition):
        return self.visit(condition) and self.visit(action)

    @v_args(inline=True)
    def params(self, p):
        return PARAM_EVAL[p.type](self._adv)

    @v_args(inline=True)
    def pincond(self, cmd):
        return PIN_CMD[cmd.type](self._e)

    @v_args(inline=True)
    def action(self, act):
        if isinstance(act, Token):
            return getattr(self._adv, act.value)()
        else:
            return self.visit(act)

    @v_args(inline=True)
    def literal(self, token):
        return LITERAL_EVAL[token.type](token.value)

    @v_args(inline=True)
    def function(self, fn, *args):
        return getattr(self._inst, fn.value)(*map(self.visit, args))

    @v_args(inline=True)
    def indice(self, fn, idx):
        if isinstance(fn, Token):
            return getattr(self._inst, fn.value)[self.visit(idx)]
        else:
            return self.visit(fn)[self.visit(idx)]

def build_acl(acl, adv):
    tree = PARSER.parse(acl)
    interpreter = AclInterpreter()
    interpreter.bind(tree, adv)
    print(acl)
    print(tree)
    print(tree.pretty())
    return interpreter

"""
changes from current:
dragon.act("c3 s end") -> dragon(c3 s end)

with exception of stuff in PIN_CMD and PARAM_EVAL, all identifiers are assumed to be attributes of self

end is now mandatory for if/elif/else/queue
"""
