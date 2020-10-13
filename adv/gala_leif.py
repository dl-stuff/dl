from core.advbase import *
from module.template import StanceAdv

def module():
    return Gala_Leif

class Gala_Leif(StanceAdv):
    conf = {}
    conf['slots.a'] = [
    'The_Shining_Overlord',
    'Flash_of_Genius',
    'Moonlight_Party',
    'The_Plaguebringer',
    'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon(c3-s-end),fsc
        `s3, not buff(s3)
        `s4, afflics.poison.get() and cancel
        `s2(shielding), s2.check()
        `s1(striking), s1.check()
        `fs, xf=3
        """
    conf['coabs'] = ['Dragonyule_Xainfried', 'Blade', 'Lin_You']
    conf['share'] = ['Curran']
        
    def prerun(self):
        self.config_stances({
            'striking': ModeManager(group='striking', x=True, s1=True, s2=True),
            'shielding': ModeManager(group='shielding', x=True, s1=True, s2=True),
        }, hit_threshold=5)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)