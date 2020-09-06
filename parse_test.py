import sys

from find import get_acl
from core.acl import PARSER

def show(adv, acl, res=True):
    try:
        result = PARSER.parse(acl)
        if res:
            print(acl)
            print("-"*140)
            print(result)
            print(result.pretty())
    except Exception as e:
        print(adv, str(e))
        print("-"*140)

if __name__ == '__main__':
    acl_map = get_acl()
    if len(sys.argv) > 1:
        adv = sys.argv[1]
        acl = acl_map[adv]
        show(adv, acl)
    else:
        test = """
        `dragon(c3 s s end)
        `s1
        """
        show('test', test)

        # for adv, acl in acl_map.items():
        #     show(adv, acl, res=False)
