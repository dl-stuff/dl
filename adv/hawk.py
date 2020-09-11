from core.advbase import *
from slot.a import *

def module():
    return Hawk

conf_fs_alt = {
    'fs_a.attr': [
        {'dmg': 0.26, "sp": 2400, "afflic": ["poison", 120, 0.582]},
        {'dmg': 0.26, "afflic": ["stun", 110]},
        {'dmg': 0.26}, 17
    ],
    'fs_a.iv': 0.5
}
class Hawk(Adv):    
    conf = conf_fs_alt.copy()
    conf['slots.a'] = Resounding_Rendition()+The_Fires_of_Hate()
    conf['acl'] = """
        # queue self.duration<=60 and prep and self.afflics.stun.resist
        # s2; s3; fs; s1, fsc; fs; s1, fsc; s1, cancel; s2, cancel
        # end
        `s3, not buff(s3)
        `dragon(c3-s-end), s and self.duration >= 120
        `s2, self.fs_alt.uses=0 or self.s2.phase=1
        `fs, (s1.check() and self.fs_alt.uses>1) or (x=4 and self.s2.phase=0 and self.fs_alt.uses>0)
        `s1, fsc or s=1
        `s4, s or x=5
    """

    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Sylas']
    conf['share'] = ['Curran']
    conf['afflict_res.stun'] = 80
    conf['afflict_res.poison'] = 0

    def prerun(self):
        self.fs_alt = FSAltBuff(group='a', uses=2)

    def s2_proc(self, e):
        if e.group == 0:
            self.fs_alt.on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
