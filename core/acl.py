import os
from lark import Lark, Transformer


lark_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'acl.lark')
with open(lark_file) as f:
    PARSER = Lark(f.read())


class AclTransformer(Transformer):
    pass 


FORM = AclTransformer()

class AclBase:
    ADV = None
    def __init__(self, acl):
        self.acl_str = acl
        self.tree = FORM.transform(PARSER.parse(acl))

    def bind(self, adv=None):
        AclBase.ADV = adv

class AclAction:
    pass


def build_acl(acl):
    PARSER.parse

# changes from current
# dragon.act("c3 s end") -> dragon(c3 s end)
# .s3 is same as self.s3
if __name__ == '__main__':
    test1 = """
        `dragon(c3 s s end),s
        `s3, not .s3_buff and x=5
        `s1
        `s4,cancel
        `s2,x=5
    """

    test2 = """
        queue not self.s3_buff
        `s3;s1;s2;s4
        `end
        `dragon(c3 s s end),s=2
        queue prep and self.afflics.burn.get()
        `s2;s4;s1
        end
        queue prep and not self.afflics.burn.get()
        `s1;s2;s4
        end
        `s2, self.afflics.burn.get()
        `s4, fsc
        `s1, fsc
        `fs, x=3
    """

    result = PARSER.parse(test2)
    print(result)
    print(result.pretty())
