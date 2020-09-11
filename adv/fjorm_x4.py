from core.advbase import *
from slot.a import *
from slot.d import Leviathan
import adv.fjorm

def module():
    return Fjorm

class Fjorm(adv.fjorm.Fjorm):
    a3 = [('prep',1.00), ('scharge_all', 0.05)]
    conf = {}
    conf['slots.a'] = Unexpected_Requests()+Valiant_Crown()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Leviathan()
    conf['acl'] = """
        queue
        `s4
        `s2
        `s1
        `dragon
        `stop
        end
    """
    conf['coabs'] = ['Blade', 'Dagger2', 'Axe2']
    conf['share'] = ['Yue']
    conf['afflict_res.bog'] = 80

    def prerun(self):
        self.dragonform.charge_gauge(500)

    def s2_before(self, e):
        for _ in range(4):
            Selfbuff('last_bravery',0.3,15).on()
            Selfbuff('last_bravery_defense', 0.40, 15, 'defense').on()

    def s2_proc(self, e):
        self.dmg_make(f'{e.name}_reflect', 3792*8, fixed=True)

    def post_run(self, end):
        self.comment = f'4x Fjorm in {now():.02f}s with sufficient dprep'

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(Fjorm, *sys.argv)
