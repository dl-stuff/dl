from core.advbase import *
from slot.a import *
from slot.d import *
from module.template import StanceAdv


def module():
    return Lazry


class Lazry(StanceAdv):
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+His_Clever_Brother()
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon(c3-s-end)
        `s3
        `s4
        `s2(high)
        `s1(low), afflics.frostbite.timeleft()<7
        `s1(high)
    """
    conf['coabs'] = ['Blade', 'Xander', 'Summer_Estelle']
    conf['afflict_res.frostbite'] = 0
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

    def prerun(self):
        self.config_stances({
            'low': ModeManager('low', s1=True, s2=True),
            'high': ModeManager('high', s1=True, s2=True)
        }, hit_threshold=0)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
