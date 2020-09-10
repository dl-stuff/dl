import sys

from find import get_acl
from core.acl import build_acl

class FakeAdv:
    duration = 180
    def __init__(self):
        self.s3_buff = False

    def s(self, n):
        print(f'Called s{n}')
        if n == 3:
            self.s3_buff = True
        return True

    def fn(self, *args):
        print('Call with', args)
        return True

    def fs(self):
        return True

    def buff(self, *args):
        return self.s3_buff


class FakeE:
    def __init__(self, pin, dname, dstat, didx):
        self.pin = pin
        self.dname = dname
        self.dstat = dstat
        self.didx = didx


def show(adv, acl, prn=True, run=False):
    try:
        fake = FakeAdv()
        interpreter = build_acl(acl)
        interpreter.reset(fake)
        event = FakeE('fs', 'fs', None, 5)
        if prn:
            print(interpreter._tree)
            print(interpreter._tree.pretty())
        if run:
            interpreter(event)
    except Exception as e:
        print(adv)
        raise e

if __name__ == '__main__':
    acl_map = get_acl()
    if len(sys.argv) > 1:
        adv = sys.argv[1]
        acl = acl_map[adv]
        show(adv, acl)
    else:
        test = """
        `s3, not buff(s3) and fsc
        `s2
        """
        show('test', test, run=True)

        # for adv, acl in acl_map.items():
        #     show(adv, acl, prn=False, run=False)

