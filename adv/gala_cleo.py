from core.advbase import *
from slot.a import *
from slot.d import *

import random
random.seed()

def module():
    return Gala_Cleo

gleo_fs = {
    'fs_zone': {
        'dmg': 0, 'sp': 0, 'hit': 0,
        'charge': 0.5,
        'startup': 0.333,
        'recovery': 1
    }
}

class Gala_Cleo(Adv):
    comment = '(the true cleo is here)'
    conf = gleo_fs.copy()
    conf['slots.a'] = Candy_Couriers()+Primal_Crisis()  # wand c2*1.08 = 217
    conf['acl'] = """
        `dragon(c3-s-end), x=5 and self.trickery <= 1
        `s3, not self.s3_buff
        `fs, s1.charged>=s1.sp and self.fs_alt.uses > 0
        if x=5 or x=4 or fsc or s
        `s4
        `s2
        end
        `s1, s or fsc

        # Buffbot Gleo
        # https://wildshinobu.pythonanywhere.com/ui/dl_simc.html?conf=eyJhZHYiOiJnYWxhX2NsZW8iLCJkcmEiOiJSYW1pZWwiLCJ3ZXAiOiJBZ2l0bzJfSml1X0NpIiwid3AxIjoiQ2FuZHlfQ291cmllcnMiLCJ3cDIiOiJNZW1vcnlfb2ZfYV9GcmllbmQiLCJzaGFyZSI6WyJTdW1tZXJfQ2xlbyJdLCJjb2FiIjpbIklleWFzdSIsIkJvdyIsIkF1ZHJpYyJdLCJ0IjoiMTIwIiwidGVhbWRwcyI6IjMwMDAwIiwiYWNsIjoiYGRyYWdvbi5hY3QoJ3MgZW5kJyksIHM9MlxuYHMzLCBub3Qgc2VsZi5zM19idWZmXG5gZnMsIChzMS5jaGVjaygpIG9yIHMyLmNoZWNrKCkpIGFuZCBzZWxmLmZzX2FsdC51c2VzID4gMFxuYHMyLCBjYW5jZWxcbmBzMSwgY2FuY2VsXG5gczQsIHM9MSIsImNvbmRpdGlvbiI6eyJhMSBidWZmIGZvciAxMHMiOnRydWUsImJ1ZmYgYWxsIHRlYW0iOnRydWUsImhpdDE1Ijp0cnVlfX0=
        """
    conf['coabs'] = ['Blade','Bow','Dagger']
    conf['share'] = ['Curran']

    def fs_proc(self, e):
        if e.group == 'zone' and self.a1_buffed:
            Teambuff('a1_str',0.25,10).zone().on()

    def prerun(self):
        self.a1_buffed = self.condition('a1 buff for 10s')
        self.phase['s1'] = 0
        self.fs_alt = FSAltBuff(self, 'zone', uses=1)

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.phase[dst] = 0
        adv.fs_alt = Dummy()
        adv.rebind_function(Gala_Cleo, 's1_dmg')

    def s1_dmg(self, t):
        self.dmg_make(t.name,0.88)
        self.add_hits(1)
        self.dmg_make(t.name,2.65)
        self.add_hits(1)

    def s1_proc(self, e):
        self.phase[e.name] += 1
        for i in range(0, 3 + self.phase[e.name]):
            s1_timer = Timer(self.s1_dmg)
            s1_timer.name = e.name
            s1_timer.on((42.0 + 12*i )/60)
        self.fs_alt.on()
        self.phase[e.name] %= 3

    def s2_proc(self, e):
        Debuff(e.name, 0.10, 20).on()
        Debuff(e.name, 0.05, 20, 1, 'attack').on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
