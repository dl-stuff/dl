from core.advbase import *


class Summer_Mikoto(Adv):
    def prerun(self):
        self.sun = Selfbuff('sun', 1, -1, 'sunlight')
        self.wave = Selfbuff('wave', 1, -1, 'wavelight')
        self.light = self.sun.on()
        self.illuminating_sun = Selfbuff('illuminating_sun', 1, -1, 'sunlight')
        self.celestial_wave = Selfbuff('celestial_wave', 1, -1, 'wavelight')
        Timer(self.a1_light_switch, 12, True).on()

    def a1_light_switch(self, t):
        if self.light == self.sun:
            self.sun.off()
            self.wave.on()
            self.light = self.wave
        else:
            self.sun.on()
            self.wave.off()
            self.light = self.sun

    def sun_and_wave(self):
        return self.illuminating_sun.get() and self.celestial_wave.get()

    def a1_reset_sun_and_wave(self):
        self.current_s['s1'] = 'default'
        self.current_s['s2'] = 'default'
        self.illuminating_sun.off()
        self.celestial_wave.off()

    def s1_proc(self, e):
        if e.group == 'light':
            self.a1_reset_sun_and_wave()

    def s2_proc(self, e):
        if e.group == 'light':
            self.a1_reset_sun_and_wave()

    def fs_proc(self, e):
        if self.light == self.sun:
            self.illuminating_sun.on()
        else:
            self.celestial_wave.on()
        if self.sun_and_wave():
            self.current_s['s1'] = 'light'
            self.current_s['s2'] = 'light'

variants = {None: Summer_Mikoto}
