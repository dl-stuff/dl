from core.advbase import *

def module():
    return Ilia

class Ilia(Adv):
    def prerun(self):
        Event('dodge').listener(self.l_dodge_attack, order=0)
        self.alchemy = 0
        self.cartrige = 0
        o_s2_check = self.a_s_dict['s2'].check
        self.a_s_dict['s2'].check = lambda: o_s2_check() and self.alchemy > 33
        self.cartrige_fs = [
            FSAltBuff('s2_cartrige', 'cartrige1', uses=1),
            FSAltBuff('s2_cartrige', 'cartrige2', uses=1),
            FSAltBuff('s2_cartrige', 'cartrige3', uses=1)
        ]
        self.cartrige_t = Timer(self.l_cartrige_timeout)

    def a_update(self, add):
        if self.cartrige == 0:
            if add > 0 and self.hits >= 30:
                add *= 3
            prev_charge = self.alchemy // 33
            self.alchemy = min(self.alchemy+add, 100)
            if prev_charge < self.alchemy // 33:
                log('alchemy', self.alchemy // 33, self.alchemy)

    def a_deplete_cartrige(self, name, consume=1):
        if self.cartrige > 0:
            prev_cartrige = self.cartrige
            self.cartrige -= consume
            for i in range(min(3, prev_cartrige - self.cartrige)):
                if name[0] == 's':
                    Selfbuff('a3_crit', 0.3, 15, 'crit', 'chance').on()
                else:
                    Selfbuff('a3_crit', 0.3, 15, 'crit', 'chance').ex_bufftime().on()
            if self.cartrige > 0:
                self.current_s['s1'] = 'cartrige'
                self.current_s['s2'] = 'cartrige'
            else:
                self.current_s['s1'] = 'default'
                self.current_s['s2'] = 'default'
            log('cartrige', self.cartrige)

    def l_cartrige_timeout(self, t):
        self.cartrige = 0
        self.current_s['s1'] = 'default'
        self.current_s['s2'] = 'default'
        for buff in self.cartrige_fs:
            buff.off()

    def l_dodge_attack(self, e):
        log('cast', 'd')
        for _ in range(7):
            self.dmg_make('dodge', 0.10)
        self.a_update(1)

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None):
        if name in ('x1', 'x2'):
            self.a_update(1)
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit)

    def s1_before(self, e):
        if e.group == 'cartrige':
            self.a_deplete_cartrige(e.name)

    def s2_before(self, e):
        if e.group == 'cartrige':
            self.a_deplete_cartrige(e.name)
        else:
            self.cartrige = self.alchemy // 33
            self.cartrige_fs[self.cartrige-1].on()
            self.cartrige_t.on(20)
            self.current_s['s1'] = 'cartrige'
            self.current_s['s2'] = 'cartrige'

    def fs_cartrige1_before(self, e):
        self.a_deplete_cartrige(e.name, consume=1)

    def fs_cartrige2_before(self, e):
        self.a_deplete_cartrige(e.name, consume=2)

    def fs_cartrige3_before(self, e):
        self.a_deplete_cartrige(e.name, consume=3)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
