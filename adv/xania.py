from core.advbase import *
# from slot.a import *

def module():
    return Xania

class Xania(Adv):
    conf = {}
    # conf['slots.a'] = Candy_Couriers()+Me_and_My_Bestie()
    conf['slots.a'] = ['Candy_Couriers', 'Me_and_My_Bestie']
    conf['acl'] = """
        `dragon(c3-s-s-end),s
        `s3, not buff(s3) and x=5
        `s1
        `s4,cancel
        `s2,x=5
        """
    conf['coabs'] = ['Blade', 'Marth', 'Joe']
    conf['share'] = ['Kleimann']
    conf['afflict_res.burn'] = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
