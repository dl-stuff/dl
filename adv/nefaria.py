from core.advbase import *
from slot.a import *

def module():
    return Nefaria

conf_fs_alt = {
    'fs_blind.dmg':7.90,
    'fs_blind.hit':19,
    'fs_blind.sp':2400,
    'fs_blind.iv': 0.5
}
class Nefaria(Adv):
    comment = 's2 fs(precharge) s1 s1'
    
    conf = conf_fs_alt.copy()
    conf['slots.a'] = Forest_Bonds()+The_Fires_of_Hate()
    conf['slots.poison.a'] = conf['slots.a']
    conf['acl'] = """
        `dragon(c3-s-end)
        `s3, not self.s3_buff and x=4
        `fs, self.fs_alt.uses > 0 and x=4
        `s1, fsc or x=1 or not self.s3_buff
        `s4
        `s2
        """
    conf['coabs'] = ['Wand','Gala_Alex','Heinwald']
    conf['share'] = ['Curran']

    conf['afflict_res.blind'] = 80
    conf['afflict_res.poison'] = 0

    def fs_proc(self, e):
        if e.suffix == 'blind':
            self.afflics.blind('s2_fs', 110)
    
    def prerun(self):
        self.fs_alt = FSAltBuff(self, 'blind', uses=1)
        
    def s1_proc(self, e):
        with KillerModifier('s1killer', 'hit', 0.74, ['blind', 'poison']):
            self.dmg_make(e.name,1.06)
            self.add_hits(1)
            self.afflics.poison(e.name, 70, 0.582)
            self.dmg_make(e.name,7*1.06)
            self.add_hits(7)

    def s2_proc(self, e):
        self.fs_alt.on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
