from core.advbase import *
import adv.hunter_sarisse


def module():
    return Hunter_Sarisse

class Hunter_Sarisse(adv.hunter_sarisse.Hunter_Sarisse):
    def prerun(self):
        super().prerun()
        self.fs_attenuation = 6

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(Hunter_Sarisse, *sys.argv)