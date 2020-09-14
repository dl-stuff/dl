from core.advbase import *
import adv.gala_alex

def module():
    return Gala_Alex

class Gala_Alex(adv.gala_alex.Gala_Alex):
    conf = adv.gala_alex.Gala_Alex.conf.copy()
    conf['acl'] = """
        queue not afflics.poison.get()
        `s2; fs, x=4
        `s1; fs, x=4
        `s2; fs, x=4
        `s1; s2
        end
        queue afflics.poison.get()
        `s1; fs, x=4
        `s2; fs, x=4
        `s1; fs, x=4
        `s2; s1
        end
    """

    def __init__(self, conf=None, cond=None):
        super().__init__(conf=conf, cond=cond, altchain='break')

    def prerun(self):
        super().prerun()
        self.duration = 10
        self.sr.charged = 1129*3
        Selfbuff('agito_s3', 0.30, -1, 'spd', 'passive').on()
        Selfbuff('agito_s3', 0.05, -1, 'crit', 'chance').on()

    def post_run(self, end):
        self.comment = f'{now():.02f}s sim; 3 charges into bk + bk killer chain; no bk def down'

    def build_rates(self):
        rates = super().build_rates()
        rates.append(('break', 1.00))
        return rates

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(Gala_Alex, *sys.argv)