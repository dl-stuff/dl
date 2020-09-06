from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Jakob

class Jakob(Adv):
    a1 = ('prep','50%')

    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Breakfast_at_Valerios()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon(c3-s-end),s
        `s3
        `s4
        `s1, cancel
        `fs, seq=5
    """
    conf['coabs'] = ['Summer_Estelle', 'Xander', 'Blade']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']
    conf['afflict_res.bog'] = 100

    def s1_proc(self, e):
        self.dmg_make(e.name,2.27)
        self.afflics.bog.on(e.name, 90)
        self.dmg_make(e.name,4.54)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
