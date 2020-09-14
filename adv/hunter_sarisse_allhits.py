from core.advbase import *
import adv.hunter_sarisse


def module():
    return Hunter_Sarisse

class Hunter_Sarisse(adv.hunter_sarisse.Hunter_Sarisse):
    conf = adv.hunter_sarisse.Hunter_Sarisse.conf.copy()
    conf['attenuation'] = -1

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(Hunter_Sarisse, *sys.argv)