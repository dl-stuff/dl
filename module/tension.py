from core.advbase import *

class Tension:
    MAX_STACK = 5
    def __init__(self, name, mod):
        # self.adv = adv
        # self.o_dmg_make = adv.dmg_make
        # self.adv.dmg_make = self.dmg_make
        self.name = name
        self.modifier = mod
        self.modifier.off()
        self.add_event = Event(name)
        self.end_event = Event(f'{name}_end')
        self.stack = 0
        self.queued_stack = 0
        self.has_stack = Selfbuff('has_'+self.name, 1, -1, 'effect')
        self.active = set()
        self.disabled = False
        self.extra_tensionable = set()

    def add(self, n=1, team=False, queue=False):
        if self.disabled:
            return
        if team:
            log(self.name, 'team', n)
        # cannot add if max stacks
        if self.stack >= self.MAX_STACK:
            if queue:
                self.queued_stack = n
            return
        self.stack += n
        self.has_stack.on()
        if self.stack >= self.MAX_STACK:
            self.stack = self.MAX_STACK
        log(self.name, '+{}'.format(n), 'stack <{}>'.format(int(self.stack)))

        self.add_event.stack = self.stack
        self.add_event.on()

    def add_extra(self, n, team=False):
        if team:
            log('{}_extra'.format(self.name), 'team', n)
        if self.stack == self.MAX_STACK:
            return
        self.stack += n
        if self.stack >= self.MAX_STACK:
            self.stack = self.MAX_STACK
        log('{}_extra'.format(self.name), '+{}'.format(n), 'stack <{}>'.format(int(self.stack)))

    def on(self, e):
        if self.stack >= self.MAX_STACK and (e.name in self.modifier._static.damage_sources or e.name in self.extra_tensionable):
            log(self.name, 'active', 'stack <{}>'.format(int(self.stack)))
            self.active.add(e.name)
    
    def off(self, e):
        if e.name in self.active:
            self.active.discard(e.name)
            self.has_stack.off()
            self.stack = 0
            log(self.name, 'reset', 'stack <{}>'.format(int(self.stack)))
            self.end_event.on()

    allow_acl = True
    def __call__(self):
        return self.stack

class Energy(Tension):
    def __init__(self):
        super().__init__(
            'energy',
            mod=Modifier('mod_energized','s','passive',0.50))

class Inspiration(Tension):
    def __init__(self):
        super().__init__(
            'inspiration',
            mod=Modifier('mod_inspired','crit','chance',1.00))
