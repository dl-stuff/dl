from core.advbase import *
import adv.gala_alex

def module():
    return Gala_Alex

class Gala_Alex(adv.gala_alex.Gala_Alex):
    conf = adv.gala_alex.Gala_Alex.conf.copy()
    conf['slots.a'] = [
        'Howling_to_the_Heavens',
        'Memory_of_a_Friend',
        'The_Shining_Overlord',
        'His_Clever_Brother',
        'The_Plaguebringer'
    ]
    conf['acl'] = """
        queue
        `s1; fs, x=4
        `s2; fs, x=4
        `s1; fs, x=4
        `s2;
        `s1;
        end
    """
    conf['coabs.base'] = ['Ieyasu','Wand','Summer_Patia']
    conf['share.base'] = ['Fjorm']
    conf['sim_afflict.frostbite'] = 1

    def __init__(self, **kwargs):
        kwargs['equip_key'] = None
        super().__init__(altchain='break', **kwargs)

    def pre_conf(self, equip_key=None):
        self.conf = Conf(self.conf_default)
        self.conf.update(globalconf.get_adv(self.name))
        self.conf.update(self.conf_base)
        # equip = globalconf.load_equip_json(self.name)
        # equip_d = equip.get(str(int(self.duration)))
        # if not equip_d:
        #     equip_d = equip.get('180')
        # if equip_d:
        #     if equip_key is None:
        #         equip_key = equip_d.get('pref', 'base')
        #         self.equip_key = equip_key
        #     elif equip_key == 'affliction':
        #         from core.simulate import ELE_AFFLICT
        #         self.equip_key = 'affliction'
        #         equip_key = ELE_AFFLICT[self.conf.c.ele]
        #     if equip_key in equip_d:
        #         self.conf.update(equip_d[equip_key])
        #         self.equip_key = self.equip_key or equip_key
        #     elif 'base' in equip_d:
        #         self.conf.update(equip_d['base'])
        self.conf.update(self.conf_init)
        return None

    def prerun(self):
        super().prerun()
        self.duration = 10
        self.sr.charged = 1129*3
        Selfbuff('agito_s3', 0.30, -1, 'spd', 'passive').on()
        Selfbuff('agito_s3', 0.05, -1, 'crit', 'chance').on()
        self.hits = 100

    def post_run(self, end):
        self.comment = f'{now():.02f}s sim; 3 charges into bk + bk killer chain; no bk def adjustment'

    def build_rates(self, as_list=True):
        rates = super().build_rates(as_list=False)
        rates['break'] = 1.00
        # rates['debuff_def'] = 1.00
        # rates['poison'] = 1.00
        return rates if not as_list else list(rates.items())

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(Gala_Alex, *sys.argv)