import sys
from core.timeline import now, Timeline
import re

class Acl_Action:
    dragon_act = re.compile(r'dragon(form)?.act\(["\']([A-Za-z \*\+\d]+)["\']\)')
    def __init__(self, action):
        self._act = None
        self.args = None
        if action.startswith('dragon'):
            self.action = 'dragonform'
            res = self.dragon_act.match(action)
            if res:
                self.args = res.group(2)
        else:
            self.action = action

    def __repr__(self):
        return self.action

    def prep(self, adv):
        if self.action == 'dragonform' and self.args is not None:
            self._act = lambda: adv.dragonform.act(self.args)
        else:
            self._act = lambda: getattr(adv, self.action)()

    def do(self):
        return self._act()


class Acl_Condition:
    banned = re.compile(r'(exec|eval|compile|setattr|delattr|memoryview|property|globals|locals|open|print|__[a-zA-Z]+__).*')
    banned_repl = 'True'
    assignment = re.compile(r'([^=><!])=([^=])')
    assignment_repl = lambda s: s[1]+'=='+s[2]

    banned = re.compile(r'(exec|eval|compile|setattr|delattr|memoryview|property|globals|locals|open|print|__[a-zA-Z]+__).*')
    banned_repl = 'True'
    assignment = re.compile(r'([^=><!])=([^=])')
    assignment_repl = lambda s: s[1]+'=='+s[2]

    @staticmethod
    def sanitize_qwe_and_his_chunch_legs(condition):
        condition = Acl_Condition.banned.sub(Acl_Condition.banned_repl, condition)
        condition = Acl_Condition.assignment.sub(Acl_Condition.assignment_repl, condition)
        return condition

    def __init__(self, condition):
        self.condition = Acl_Condition.sanitize_qwe_and_his_chunch_legs(condition)
        # self.condition = condition

    def prep(self):
        self._cond = compile(self.condition, '<string>', 'eval')

    def eval(self):
        return self.condition is None or eval(self.condition, Acl_Control.CTX)


class Acl_Control:
    AQU = []
    CTX = None

    def __init__(self, condition):
        self.conditions = [(Acl_Condition(condition), [])]
        self._act_cond = None

    def add_action(self, action):
        self.conditions[-1][-1].append(action)

    def add_condition(self, condition, is_else=False):
        self.conditions.append((Acl_Condition(condition), []))

    def __repr__(self):
        return '\n'.join(f'\n<{cond}> {acts}' for cond, acts in self.conditions)

    def prep(self, adv):
        Acl_Control.AQU = []
        for cond, acts in self.conditions:
            cond.prep()
            for a in acts:
                a.prep(adv)
        if len(self.conditions) == 1:
            cond, acts = self.conditions[0]
            if len(acts) == 1 and isinstance(acts[0], Acl_Action):
                self._act_cond = acts[0], cond

    def do(self):
        for cond, acts in self.conditions:
            if cond.eval():
                for a in acts:
                    if a.do():
                        return True
                break
        return False

    @staticmethod
    def set_ctx(self, e):
        this = self
        pin, dname, dstat, didx = e.pin, e.dname, e.dstat, e.didx
        prev = self.action.getprev()
        seq = didx if dname[0] == 'x' else 0 if dstat == -2 else -1
        cancel = pin =='x' or pin == 'fs'
        x = didx if pin =='x' else 0
        fsc = pin =='fs'
        s = int(pin[1]) if (pin[0] == 's' and pin[1].isdigit()) or pin[-2:] == '-x' else 0
        sp = dname if pin == 'sp' else 0
        prep = pin == 'prep'
        sim_duration = self.duration
        Acl_Control.CTX = locals()

    def __call__(self, adv, e):
        Acl_Control.set_ctx(adv, e)
        if len(Acl_Control.AQU) > 0:
            next_act, next_cond = Acl_Control.AQU[0]
            if next_cond.eval() and next_act.do():
                return Acl_Control.AQU.pop(0)
        self.do()


class Acl_Queue(Acl_Control):
    def do(self):
        for cond, acts in self.conditions:
            if len(Acl_Control.AQU) == 0 and cond.eval():
                for a in acts:
                    if isinstance(a, Acl_Action):
                        Acl_Control.AQU.append((a._act, None))
                    elif a._act_cond:
                        Acl_Control.AQU.append(a._act_cond)
        return False


def acl_build(acl):
    root = Acl_Control('True')
    node_stack = [root]
    real_lines = []
    for line in acl.split('\n'):
        line = line.strip().replace('`', '')
        if len(line) > 0 and line[0] != '#':
            if ';' in line:
                for s in line.split(';'):
                    s = s.strip().replace('`', '')
                    if len(s) > 0 and s[0] != '#':
                        real_lines.append(s)
            else:
                real_lines.append(line)
    for line in real_lines:
        upper = line.upper()
        if upper.startswith('IF '):
            node = Acl_Control(line[3:])
            node_stack[-1].add_action(node)
            node_stack.append(node)
        elif upper.startswith('QUEUE'):
            cond = 'True' if upper == 'QUEUE' else line[6:]
            node = Acl_Queue(cond)
            node_stack[-1].add_action(node)
            node_stack.append(node)
        elif upper.startswith('ELIF '):
            node_stack[-1].add_condition(line[5:])
        elif upper.startswith('ELSE'):
            node_stack[-1].add_condition('True')
        elif upper.startswith('END'):
            node_stack.pop()
        else:
            parts = [l.strip() for l in line.split(',')]
            if len(parts) == 1 or len(parts[1]) == 0:
                action = parts[0]
                node = Acl_Action(action)
                node_stack[-1].add_action(node)
            else:
                action = parts[0]
                condition = parts[1]
                node = Acl_Control(condition)
                node_stack[-1].add_action(node)
                node.add_action(Acl_Action(action))
    return root

def acl_str(root):
    acl_base = """
def do_act_list(self, e):
    this = self
    pin, dname, dstat, didx = e.pin, e.dname, e.dstat, e.didx
    prev = self.action.getprev()
    seq = didx if dname[0] == 'x' else 0 if dstat == -2 else -1
    cancel = pin =='x' or pin == 'fs'
    x = didx if pin =='x' else 0
    fsc = pin =='fs'
    s = int(pin[1]) if (pin[0] == 's' and pin[1] in ('1', '2', '3')) or pin[-2:] == '-x' else 0
    sp = dname if pin == 'sp' else 0
    prep = pin == 'prep'
    sim_duration = self.duration
{act_prep_block}
    if len(self.acl_queue) > 0:
        next_act, next_cond = self.acl_queue[0]
        if eval(next_cond) and next_act():
            self.acl_queue.pop(0)
        return 'queue'
{act_cond_block}
    return 0"""
    acl_string = acl_base.format(
        act_prep_block=root.prepare(),
        act_cond_block=root.act()
    )
    return acl_string