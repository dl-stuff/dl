from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Mikoto

class Mikoto(Adv):
    a1 = ('cc',0.10,'hp70')
    a3 = ('cc',0.08)
    
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+The_Fires_of_Hate()
    conf['slots.burn.a'] = Resounding_Rendition()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon, s=2 
        queue prep
        `s4;s1;s2
        end
        `s3, not buff(s3)
        `s4
        `s1, cancel
        `s2, x=5
        """
    conf['coabs'] = ['Halloween_Mym', 'Dagger2', 'Marth']
    conf['share'] = ['Kleimann']

    def prerun(self):
        self.s1buff = Selfbuff('s1',0.0, 20)
        self.conf.s1.recovery = 1.4

    def s1latency(self, e):
        self.s1buff.off()
        self.s1buff.on()

    def s1_proc(self, e):
        buff = self.s1buff.get()
        if buff == 0:
            stance = 0
        elif buff == 0.10:
            stance = 1
        elif buff == 0.15:
            stance = 2
        if stance == 0:
            self.dmg_make(e.name,5.32*2)
            self.s1buff.set(0.10,20) #.on()
            self.conf.s1.recovery = 1.4
            Timer(self.s1latency).on(1.5/self.speed())
        elif stance == 1:
            self.dmg_make(e.name,3.54*3)
            self.s1buff.off()
            self.s1buff.set(0.15,15) #.on()
            self.conf.s1.recovery = 1.63
            Timer(self.s1latency).on(1.5/self.speed())
        elif stance == 2:
            self.dmg_make(e.name,2.13*3+4.25)
            self.s1buff.off().set(0)
            self.conf.s1.recovery = 3.07

    def s2_proc(self, e):
        Spdbuff(e.name, 0.2, 10).on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
