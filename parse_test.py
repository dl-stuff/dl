import sys

from find import get_acl
from core.acl import build_acl

class FakeAdv:
    duration = 180
    bolb = {'s1': False}
    def __init__(self):
        self.s3_buff = False

    def s1(self):
        print('Called s1')
        return True

    def s2(self):
        print('Called s2')
        return True

    def s3(self):
        print('Called s3')
        return False

    def fn(self, *args):
        print('Call with', args)
        return True

    def rd(self):
        return {'s3': 33333}


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
        event = FakeE('x', 'x5_missile', None, 5)
        if prn:
            print(interpreter._tree)
            print(interpreter._tree.pretty())
        if run:
            interpreter.run(event)
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
        # test = """
        # queue prep and not self.afflics.burn.get()
        # `s1
        # end
        # """
        # show('test', test, run=False)

        for adv, acl in acl_map.items():
            show(adv, acl, prn=False, run=False)

