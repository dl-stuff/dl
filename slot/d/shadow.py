from slot import *
from math import ceil

class Marishiten(DragonBase):
    ele = 'shadow'
    att = 121
    a = [('a', 0.6)]
    dragonform = {
        'act': 'c5-c5-s-c4',

        'dx1.dmg': 2.20,
        'dx1.startup': 25 / 60.0, # c1 frames
        'dx1.hit': 1,

        'dx2.dmg': 2.31,
        'dx2.startup': 32 / 60.0, # c2 frames
        'dx2.hit': 1,

        'dx3.dmg': 2.44,
        'dx3.startup': 53 / 60.0, # c3 frames
        'dx3.hit': 2,

        'dx4.dmg': 2.55,
        'dx4.startup': 26 / 60.0, # c4 frames
        'dx4.hit': 1,

        'dx5.dmg': 3.22,
        'dx5.startup': 69 / 60.0, # c5 frames
        'dx5.recovery': 720 / 60.0, # recovery unknown but longer than dodge
        'dx5.hit': 2,

        'ds.recovery': 228 / 60, # skill frames
        'ds.hit': 6,

        'dodge.startup': 45 / 60, # dodge frames
    }

    def oninit(self, adv):
        super().oninit(adv)
        from module.bleed import Bleed
        self.bleed = Bleed('ds', 1.46).reset()

    def ds_proc(self):
        dmg = self.adv.dmg_make('ds',1.04,'s')
        self.bleed.on()
        return dmg + self.adv.dmg_make('ds',5.20,'s')

class Shinobi(DragonBase):
    ele = 'shadow'
    att = 128
    a = [('s', 0.9), ('a', 0.2)]
    dragonform = {
        'act': 'c3-s',
        # 'dshift.startup': 88 / 60, # shift 98 -> 88 + 10

        'dx1.dmg': 1.50,
        'dx1.startup': 16 / 60.0, # c1 frames
        'dx1.hit': 2,

        'dx2.dmg': 2.46,
        'dx2.startup': 24 / 60.0, # c2 frames
        'dx2.hit': 6,

        'dx3.dmg': 2.88,
        'dx3.startup': 31 / 60.0, # c3 frames
        'dx3.recovery': 60 / 60.0, # recovery
        'dx3.hit': 8,

        'ds.recovery': 88 / 60, # skill frames
        'ds.hit': 0,

        'dodge.startup': 33 / 60, # dodge frames
    }

    def ds_proc(self):
        count = self.adv.dmg_make('ds',8.83,'s')
        self.adv.energy.add(5, team=True)
        return count

class Fatalis(DragonBase):
    ele = 'shadow'
    att = 128
    a = [('a', 0.8)]
    dragonform = {
        'act': 'c3-s',

        'dx1.dmg': 2.15,
        'dx1.startup': 24 / 60.0, # c1 frames
        'dx1.hit': 1,

        'dx2.dmg': 2.58,
        'dx2.startup': 40 / 60.0, # c2 frames
        'dx2.hit': 1,

        'dx3.dmg': 4.03,
        'dx3.startup': 64 / 60.0, # c3 frames
        'dx3.recovery': 720 / 60.0, # unknown
        'dx3.hit': 2,

        'ds.dmg': 5.01,
        'ds.recovery': 189 / 60, # skill frames
        'ds.hit': 3,

        'dodge.startup': 41 / 60, # dodge frames
    }

    def oninit(self, adv):
        super().oninit(adv)
        adv.dragonform.disabled = True
        def permanent_curse(e):
            if hasattr(adv, 'afflict_guard') and adv.afflict_guard > 0:
                adv.afflict_guard -= 1
            else:
                adv.skill._static.silence = 1
                adv.dragonform.disabled = True
                from core.log import log
                log('debug', 'permanent_curse')
        from core.timeline import Event
        Event('dragon').listener(permanent_curse)


class Nyarlathotep(DragonBase):
    ele = 'shadow'
    att = 128
    a = [('a', 0.5, 'hp30')]
    dragonform = {
        'act': 'c2 s c2 c2 c2 c2 c2 c1',

        'dx1.dmg': 2.10,
        'dx1.startup': 20 / 60.0, # c1 frames
        'dx1.hit': 1,

        'dx2.dmg': 2.31,
        'dx2.startup': 42 / 60.0, # c2 frames
        'dx2.hit': 1,

        'dx3.dmg': 2.74,
        'dx3.startup': 71 / 60.0, # c3 frames
        'dx3.recovery': 70 / 60.0, # recovery
        'dx3.hit': 2,

        'ds.dmg': 7.36,
        'ds.recovery': 129 / 60, # skill frames
        'ds.hit': 2,

        'dodge.startup': 41 / 60, # dodge frames
    }

    def oninit(self, adv):
        super().oninit(adv)
        self.bloody_tongue(0)
        buff_rate = 90
        if adv.condition('low HP every {}s'.format(buff_rate)):
            buff_times = ceil(adv.duration/buff_rate)
            for i in range(1, buff_times):
                adv.Timer(self.bloody_tongue).on(buff_rate*i)

    def bloody_tongue(self, t):
        self.adv.Buff('bloody_tongue',0.30, 20).on()

class Chthonius(DragonBase):
    ele = 'shadow'
    att = 128
    a = [('a',0.55), ('dm', 1)]
    dragonform = {
        'act': 'c3-s',

        'dx1.dmg': 2.10,
        'dx1.startup': 21 / 60.0, # c1 frames
        'dx1.hit': 1,

        'dx2.dmg': 2.52,
        'dx2.startup': 41 / 60.0, # c2 frames
        'dx2.hit': 1,

        'dx3.dmg': 3.58,
        'dx3.startup': 86 / 60.0, # c3 frames
        'dx3.recovery': 55 / 60.0, # recovery
        'dx3.hit': 2,

        'ds.recovery': 110 / 60, # skill frames
        'ds.hit': 1,

        'dodge.startup': 41 / 60, # dodge frames
    }

    def ds_proc(self):
        dmg = self.adv.dmg_make('ds',4.90,'s')
        self.adv.afflics.poison('ds',120,0.582,dtype='s')
        return dmg

class Epimetheus(DragonBase):
    ele = 'shadow'
    att = 128
    a = [('k_poison', 0.2), ('a', 0.5)]
    dragonform = {
        'act': 'c3-s',

        'dx1.dmg': 1.80,
        'dx1.startup': 14 / 60.0, # c1 frames
        'dx1.hit': 1,

        'dx2.dmg': 1.98,
        'dx2.startup': 36 / 60.0, # c2 frames
        'dx2.hit': 1,

        'dx3.dmg': 2.52,
        'dx3.startup': 38 / 60.0, # c3 frames
        'dx3.recovery': 50 / 60.0, # recovery
        'dx3.hit': 2,

        'ds.recovery': 123 / 60, # skill frames
        'ds.hit': 1,

        'dodge.startup': 41 / 60, # dodge frames
    }

    def ds_proc(self):
        dmg = self.adv.dmg_make('ds',6.30,'s')
        self.adv.afflics.poison('ds',120,0.291,30,dtype='s')
        return dmg


class Andromeda(DragonBase):
    ele = 'shadow'
    att = 128
    a = [('a', 0.4), ('a', 0.4, 'hp<30')]
    dragonform = {
        'act': 'c3-s',

        'dx1.dmg': 1.90,
        'dx1.startup': 20 / 60.0, # c1 frames
        'dx1.hit': 1,

        'dx2.dmg': 2.09,
        'dx2.startup': 44 / 60.0, # c2 frames
        'dx2.hit': 1,

        'dx3.dmg': 3.24,
        'dx3.startup': 44 / 60.0, # c3 frames
        'dx3.recovery': 65 / 60.0, # recovery
        'dx3.hit': 3,

        'ds.recovery': 110 / 60, # skill frames
        'ds.hit': 1,

        'dodge.startup': 33 / 60, # dodge frames
    }

    def ds_proc(self):
        from core.advbase import Teambuff
        dmg = self.adv.dmg_make('ds',6.60,'s')
        Teambuff('ds', 0.30, 15, 'defense').on()
        return dmg


class Azazel(DragonBase):
    ele = 'shadow'
    att = 128
    a = [('sp', 0.35)]
    dragonform = {
        'act': 'c3-s',

        'dx1.dmg': 1.90,
        'dx1.startup': 12 / 60.0, # c1 frames
        'dx1.hit': 1,

        'dx2.dmg': 2.09,
        'dx2.startup': 36 / 60.0, # c2 frames
        'dx2.hit': 1,

        'dx3.dmg': 3.24,
        'dx3.startup': 39 / 60.0, # c3 frames
        'dx3.recovery': 56 / 60.0, # recovery
        'dx3.hit': 3,

        'ds.recovery': 130 / 60, # skill frames, need confirm
        'ds.hit': 1,
    }

    def ds_proc(self):
        from core.advbase import Teambuff
        self.adv.afflics.poison('ds',120,0.291,30,dtype='s')
        dmg = self.adv.dmg_make('ds',5.00,'s')
        Teambuff('ds', 0.15, 40, 'poison_killer', 'passive').on()
        return dmg

class Gala_Cat_Sith(DragonBase):
    ele = 'shadow'
    att = 128
    a = []
    dragonform = {
        'act': 'c3-s',

        'dx1.dmg': 3.00,
        'dx1.startup': 18 / 60.0, # c1 frames
        'dx1.hit': 1,

        'dx2.dmg': 3.60,
        'dx2.startup': 55 / 60.0, # c2 frames
        'dx2.hit': 1,

        'dx3.dmg': 4.50,
        'dx3.startup': 43 / 60.0, # c3 frames
        'dx3.recovery': 56 / 60.0, # recovery
        'dx3.hit': 1,

        'ds.dmg': 7.744,
        'ds.recovery': 90 / 60,
        'ds.hit': 32,
    }

    def oninit(self, adv):
        super().oninit(adv)
        from core.advbase import Event, SingleActionBuff
        Event('dragon_end').listener(self.shift_end_trickery)
        self.max_trickery = 14 # 1 trickery is in the buff at all times
        self.adv.trickery = self.max_trickery
        self.threshold = 25
        self.trickery_buff = SingleActionBuff('d_trickery_buff', 1.80, 1,'s', 'buff').on()
        self.check_trickery()

        if adv.condition('always connect hits'):
            self.add_combo_o = adv.add_combo
            self.thit = 0
            def add_combo(name=None):
                self.add_combo_o(name)
                if adv.hits == 0:
                    self.thit = 0
                else:
                    n_thit = adv.hits // self.threshold
                    if n_thit > self.thit:
                        self.add_trickery(1)
                        self.thit = n_thit
                self.check_trickery()
            adv.add_combo = add_combo

    def add_trickery(self, t):
        from core.log import log
        log('debug', 'trickery', f'+{t}', self.adv.trickery, self.adv.hits)
        self.adv.trickery = min(self.adv.trickery+t, self.max_trickery)

    def check_trickery(self, e=None):
        from core.log import log
        if self.adv.trickery > 0 and not self.trickery_buff.get():
            self.adv.trickery -= 1
            log('debug', 'trickery', 'consume', self.adv.trickery)
            self.trickery_buff.on()

    def shift_end_trickery(self, e):
        if not self.adv.dragonform.is_dragondrive:
            self.add_trickery(8)

class Ramiel(DragonBase):
    ele = 'shadow'
    att = 128
    a = [('a', 0.6), ('dp', 50)]
    # need framedata
    dragonform = {
        'act': 'c3-s',

        'dx1.dmg': 1.95,
        'dx1.startup': 20 / 60.0, # c1 frames
        'dx1.hit': 1,

        'dx2.dmg': 2.35,
        'dx2.startup': 40 / 60.0, # c2 frames
        'dx2.hit': 1,

        'dx3.dmg': 3.40,
        'dx3.startup': 55 / 60.0, # c3 frames
        'dx3.recovery': 45 / 60.0, # recovery
        'dx3.hit': 1,

        'ds.recovery': 220 / 60,
        'ds.hit': -2,
    }

    def oninit(self, adv):
        super().oninit(adv)
        from core.advbase import Debuff, EffectBuff, Timer
        self.sp_convert = adv.sp_convert
        self.s1 = adv.s1
        self.s2 = adv.s2
        self.ds_buff = Debuff('ds',-0.20,15)
        self.sp_regen_buff = EffectBuff('ds_sp', 90, lambda: self.sp_regen_timer.on(), lambda: self.sp_regen_timer.off())
        self.sp_regen_timer = Timer(self.sp_regen, 1.99, 1)

    def sp_regen(self, t):
        self.s1.charge(self.sp_convert(0.015, self.s1.sp))
        self.s2.charge(self.sp_convert(0.015, self.s2.sp))
        
    def ds_proc(self):
        dmg = self.adv.dmg_make('ds',3.224,'s')
        self.adv.afflics.poison('ds',120,0.582,dtype='s')
        self.ds_buff.on()
        self.s2.charge(self.s2.sp)
        self.sp_regen_buff.on()
        return dmg + self.adv.dmg_make('ds',4.836,'s')

class Unreleased_ShadowCritDamage(DragonBase):
    ele = 'shadow'
    att = 127
    a = [('a', 0.45), ('cd', 0.55)]

class Unreleased_ShadowPrimedStr(DragonBase):
    ele = 'shadow'
    att = 127
    a = [('primed_att', 0.15), ('a', 0.45)]
