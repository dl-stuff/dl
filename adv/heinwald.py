from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Heinwald

class Heinwald(Adv):
    a1 = ('s',0.4,'hp70')
    a3 = [('prep',1.00), ('scharge_all', 0.05)]
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+The_Fires_of_Hate()
    conf['acl'] = '''
        `dragon(c3-s-end),x=5
        queue prep and not buff(s3)
        `s3;s1;s4;s2
        end
        `s4
        `s1
        `s2, cancel
        '''
    conf['coabs'] = ['Blade','Wand','Bow']
    conf['share'] = ['Kleimann']

    def d_coabs(self):
        if self.sim_afflict:
            self.conf['share'] = ['Curran']
    
    def s2_proc(self, e):
        self.s2_buff = Selfbuff(e.name,0.25,10).on()
        if self.condition('buff all teammates'):
            Teambuff(e.name,0.15,10).on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
