from core.advbase import *
from module.x_alt import X_alt
from module.template import StanceAdv

def module():
    return Mitsuba

class Mitsuba(StanceAdv):
    conf = {}
    conf['slots.a'] = ['Twinfold_Bonds', 'His_Clever_Brother']
    conf['slots.d'] = 'Siren'
    # tc2afsf tc2a- s1
    conf['acl'] = """
        `tempura
        if xf=2
        `s4
        `s3
        `s2
        `s1(sashimi), afflics.frostbite.timeleft()<6
        `s1(tempura)
        `fsf
        end

        # buffbot mitsuba w/ G&C
        # `tempura
        # if xf=2
        # `s2
        # `s4
        # `s3
        # `fsf
        # end
    """
    conf['coabs'] = ['Blade', 'Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Eugene']
    
    def prerun(self):
        self.config_stances({
            'sashimi': ModeManager(group='sashimi', x=True, s1=True, s2=True),
            'tempura': ModeManager(group='tempura', x=True, s1=True, s2=True)
        }, hit_threshold=20)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)