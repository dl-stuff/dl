from core.advbase import *
from slot.a import *

def module():
    return Louise

class Louise(Adv):
    a1 = ('od',0.15)
    a3 = ('bc',0.15)

    conf = {}
    conf['slots.a'] = Resounding_Rendition()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end), s2.check()
        `s3, not buff(s3)
        `s2
        `s1
        `s4, fsc
        `fs, x=5
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Lin_You']
    conf['afflict_res.poison'] = 0
    conf['share'] = ['Curran']

    def s1_proc(self, e):
        self.dmg_make(e.name, 3.87)
        self.afflics.poison(e.name, 120, 0.582)
        self.dmg_make(e.name, 3.87)
        self.dmg_make(e.name, 3.87)
        self.dmg_make(e.name, 3.87)
        self.set_hp(self.hp+5)

    def s2_proc(self, e):
        with KillerModifier(e.name, 'hit', 0.5, ['poison']), CrisisModifier(e.name, -0.5, self.hp):
            self.dmg_make(e.name, 6.98)
            self.dmg_make(e.name, 6.98)
            self.dmg_make(e.name, 6.98)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)