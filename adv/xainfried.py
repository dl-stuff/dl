from core.advbase import *

def module():
    return Xainfried

class Xainfried(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'His_Clever_Brother'] # no more poison lol
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `dragon(c3-s-end)
        `s3
        `s2
        `s4
        `s1, fsc
        `fs, x=5
        """
    conf['coabs'] = ['Summer_Celliera', 'Yurius', 'Renee']
    conf['share'] = ['Gala_Elisanne', 'Eugene']
    conf['afflict_res.frostbite'] = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
