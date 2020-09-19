from core.advbase import *

def module():
    return Wedding_Aoi

class Wedding_Aoi(Adv):
    conf = {}
    conf['slots.a'] = ['Twinfold_Bonds', 'Primal_Crisis']
    conf['acl'] = """
        `dragon(c3-s-end), x=5
        `s3, not buff(s3)
        `s4
        `s1,cancel
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']
    conf['afflict_res.sleep'] = 80


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
