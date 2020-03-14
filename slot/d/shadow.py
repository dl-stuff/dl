from slot import *
from math import ceil

class Marishiten(DragonBase):
    ele = 'shadow'
    att = 121
    a = [('a', 0.6)]
    dragonform = {
        'act': 'c5 c5 s c4',

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
        self.bleed = Bleed('ds_bleed', 1.46).reset()

    def ds_proc(self):
        dmg = self.adv.dmg_make('ds',1.04,'s')
        self.bleed.on()
        return dmg + self.adv.dmg_make('ds',5.20,'s')

class Shinobi(DragonBase):
    ele = 'shadow'
    att = 128
    a = [('s', 0.9), ('a', 0.2)]
    dragonform = {
        'act': 'c3 s',
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
    att = 121
    a = [('a', 0.8)]
    dragonform = {
        'act': 'c3 s',

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
        def permanent_curse(e):
            if hasattr(adv, 'afflict_guard') and adv.afflict_guard > 0:
                adv.afflict_guard -= 1
            else:
                adv.skill._static.silence = 1
                adv.dragonform.disabled = True
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
    a = [('a',0.55)]
    dragonform = {
        'act': 'c3 s',

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

    def oninit(self, adv):
        super().oninit(adv)
        self.dm_count = 2
        def dragon_might(t):
            if self.dm_count > 0:
                self.dm_count -= 1
                self.adv.Buff('dc',0.10, -1).on()
        from core.timeline import Event
        Event('dragon').listener(dragon_might)

    def ds_proc(self):
        dmg = self.adv.dmg_make('ds',4.90,'s')
        self.adv.afflics.poison('ds',120,0.582,dtype='s')
        return dmg

class Epimetheus(DragonBase):
    ele = 'shadow'
    att = 128
    a = [('k_poison', 0.2), ('a', 0.5)]
    dragonform = {
        'act': 'c3 s',

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

class Unreleased_ShadowSkillHaste(DragonBase):
    ele = 'shadow'
    att = 120
    a = [('sp', 0.35)]

class Unreleased_ShadowPrimedStr(DragonBase):
    ele = 'shadow'
    att = 127
    a = [('primed_att', 0.15), ('a', 0.45)]

class Unreleased_DKR_No_More(DragonBase):
    ele = 'shadow'
    att = 127
    a = [('a', 0.55), ('fs', 0.60), ('sp',0.30,'fs')]