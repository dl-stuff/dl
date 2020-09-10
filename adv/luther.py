from core.advbase import *
from slot.a import *
from slot.d import *
from module.x_alt import *

def module():
    return Luther

luther_fs = {'fs_a':{}}
class Luther(Adv):
    conf = luther_fs.copy()
    conf['slots.a'] = Twinfold_Bonds()+His_Clever_Brother()
    conf ['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon(c3-s-end)
        `s1
        `s4
        `s3, cancel
        `s2, cancel
        `fs, x=5
    """
    conf['coabs'] = ['Blade', 'Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

    def fs_proc(self, e):
        e.group == 'a' and self.afflics.frostbite(e.name,120,0.41)

    def prerun(self):
        conf_fs_alt = {}
        self.fs_alt = FSAltBuff(group='a', uses=1)
        Timer(self.fs_alt_on_crit, 10, True).on()

    def fs_alt_on_crit(self, t):
        # look i dont wanna mass sim
        self.fs_alt.on()

    def s2_proc(self, e):
        Debuff(e.name, 0.05, 10, 0.9, 'attack').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
