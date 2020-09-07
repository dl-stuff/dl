from core.advbase import *
from slot.a import *

def module():
    return Lin_You

lin_fs = {
    'fs_nados.dmg': 2.59,
    'fs_nados.hit': 6
}

class Lin_You(Adv):
    conf = lin_fs.copy()
    conf['slots.a'] = The_Wyrmclan_Duo()+Primal_Crisis()
    conf['acl'] = """
        `dragon(c3-s-end)
        `s3, not self.s3_buff
        `s4
        `s2, s1.check()
        `s1
        `fs, self.hits <= 44 and self.fs_alt.uses > 0 and x=4
        """
    conf['coabs'] = ['Blade','Dragonyule_Xainfried','Axe2']
    conf['share'] = ['Curran']

    def prerun(self):
        conf_fs_alt = {'fs.dmg': 2.59, 'fs.hit': 6}
        self.fs_alt = FSAltBuff(self, 'nados', uses=3)
        self.s2_buff = Spdbuff('s2_spd',0.20, 15)

    def s1_proc(self, e):
        if self.s2_buff.get():
            self.dmg_make(f'{e.name}_powerup', 1.86*3)
            self.s2_buff.buff_end_timer.add(self.s1.ac.getstartup()+self.s1.ac.getrecovery())
            self.add_hits(3)
            self.afflics.sleep(e.name, 150)
        self.fs_alt.on()

    def s2_proc(self, e):
        self.s2_buff.on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)