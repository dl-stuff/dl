from core.advbase import *
from slot.d import *

def module():
    return Renee

class Renee(Adv):
    a1 = ('primed_crit_chance', 0.6,5)

    conf = {}
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon.act('c3 s end'), x=2
        if self.afflics.frostbite.get()
        `s3
        `s4, cancel or s1.check()
        `s1, cancel
        `s2, cancel
        else
        `s3
        `s4
        `s1, cancel
        `s2, x=1 or s
        end
        `fs, x=5
        """
    coab = ['Blade', 'Xander', 'Summer_Estelle']
    conf['afflict_res.bog'] = 100
    share = ['Gala_Elisanne', 'Eugene']

    def s1_proc(self, e):
        self.dmg_make(e.name,1.11)
        self.afflics.bog.on(e.name, 100)
        self.dmg_make(e.name,5.55)

    def s2_proc(self, e):
        Selfbuff(f'{e.name}_defense', 0.10, 5, 'defense').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
