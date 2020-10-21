from core.advbase import *

def module():
    return Kleimann

class Kleimann(Adv):
    a3 = ('s',0.35)
 
    conf = {}
    conf['slots.a'] = [
        'Candy_Couriers',
        'Flash_of_Genius',
        'Moonlight_Party',
        'The_Plaguebringer',
        'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon(c3-s-end), x=5
        `s3, not buff(s3)
        `s1
        `s2
        `s4
        `fs, self.madness_status<5 and self.madness>0
        """
    conf['coabs'] = ['Ieyasu','Gala_Alex','Delphi']
    conf['share'] = ['Curran']

    def d_coabs(self):
        if self.duration <= 60:
            self.conf['coabs'] = ['Ieyasu','Gala_Alex','Bow']

    def a1_madness_autocharge(self, t):
        for s in self.skills:
            if s.charged < s.sp:
                sp = self.madness_status * 100
                s.charge(sp)
                log('sp', s.name+'_autocharge', int(sp))
        self.set_hp(self.hp-1)

    def prerun(self):
        self.madness = 0
        self.madness_status = 0
        self.madness_timer = Timer(self.a1_madness_autocharge, 2.9, 1)

    def fs_proc(self, e):
        if self.madness > 0 and self.madness_status < 5:
            self.madness_status += 1
            self.madness -= 1
            if self.madness_status == 1:
                self.madness_timer.on()

    def s2_proc(self, e):
        if self.madness < 5:
            self.madness += 1

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
