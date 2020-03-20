import adv.adv_test
from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Chelsea

class Chelsea(Adv):
    comment = 'c1fs'
    
    conf = {}
    conf['slot.a'] = The_Lurker_in_the_Woods() + DD()
    conf['slot.d'] = Dreadking_Rathalos()
    conf['acl'] = """
        `s3, fsc and not self.s3_buff
        `s1, fsc
        `s2, fsc
        `fs, x = 1
        """

    def prerun(self):
        self.hp = 100
        self.obsession = 0
        self.s2_buffs = []

        self.a1atk = Selfbuff('a1atk',0.20,-1,'att','passive')
        self.a1spd = Spdbuff('a1spd',0.10,-1)
        self.a3 = Selfbuff('a3_str_passive',0.3,60,'att','passive')

        Event('dragon').listener(self.s2_clear)

    def s2_clear(self, e):
        for buff in self.s2_buffs:
            buff.off()
        self.s2_buffs = []
        self.a3.off()
        self.obsession = 0

    def dmg_before(self, name):
        hpold = self.hp

        if name != 's1' and self.a3.get():
            self.hp -= 3 * self.obsession

        if self.hp <= 0:
            self.hp = hpold
        elif self.hp > 100:
            self.hp = 100

        if self.hp <= 30:
            self.a1atk.on()
            self.a1spd.on()
        else:
            self.a1atk.off()
            self.a1spd.off()

    def dmg_proc(self, name, amount):
        hpold = self.hp

        if name == 's1' and self.a3.get():
            self.hp += 7

        if self.hp <= 0:
            self.hp = hpold
        elif self.hp > 100:
            self.hp = 100

        if self.hp <= 30:
            self.a1atk.on()
            self.a1spd.on()
        else:
            self.a1atk.off()
            self.a1spd.off()

    def s1_proc(self, e):
        hpold = self.hp

        if self.a3.get():
            self.hp -= 3 * self.obsession

        if self.hp <= 0:
            self.hp = hpold
        elif self.hp > 100:
            self.hp = 100

        if self.hp <= 30:
            self.a1atk.on()
            self.a1spd.on()
        else:
            self.a1atk.off()
            self.a1spd.off()

        self.dmg_make('s1',1.36)
        self.hits += 1
        self.dmg_make('s1',1.36)
        self.hits += 1
        self.dmg_make('s1',1.36)
        self.hits += 1
        self.dmg_make('s1',1.36)
        self.hits += 1
        self.dmg_make('s1',1.36)
        self.hits += 1
        self.dmg_make('s1',1.36)
        self.hits += 1
        self.dmg_make('s1',1.36)
        self.hits += 1

    def s2_proc(self, e):
        self.s2_buffs.append(Selfbuff('s2',0.3,60).on())
        self.obsession = Selfbuff('s2').stack()
        self.a3.on()

    def dmg_make(self, name, dmg_coef, dtype=None, fixed=None):
        if dtype == None:
            dtype = name
        self.dmg_before(name)
        count = self.dmg_formula(dtype, dmg_coef)
        log('dmg', name, count)
        self.dmg_proc(name, count)
        return count

if __name__ == '__main__':
    conf = {}
    adv.adv_test.test(module(), conf)
