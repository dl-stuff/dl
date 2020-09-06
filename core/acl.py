import os
from lark import Lark, Transformer


lark_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'acl.lark')
with open(lark_file) as f:
    PARSER = Lark(f.read())


class AclInterpreter(Transformer):
    pass 


INTERPRET = AclInterpreter()


def build_acl(acl):
    PARSER.parse

"""
changes from current:
dragon.act("c3 s end") -> dragon(c3 s end)

with exception of stuff in pincond, all identifiers are assumed to be attributes of self

"""
