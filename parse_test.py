import sys

from find import get_acl
from core.acl import PARSER

def show(adv, acl, res=True):
    try:
        result = PARSER.parse(acl)
        if res:
            print(result)
            print(result.pretty())
    except Exception as e:
        print(adv, str(e))

if __name__ == '__main__':
    acl_map = get_acl()
    if len(sys.argv) > 1:
        adv = sys.argv[1]
        acl = acl_map[adv]
        show(adv, acl)
    else:
        test = """
        if cond1
        `s1
        `s2
            if cond2
            `fs
            end
        else
            if cond3
            `s3
            end
        end
        """
        show('test', test)
        exit()
        for adv, acl in acl_map.items():
            show(adv, acl, res=False)
