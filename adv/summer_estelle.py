from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Summer_Estelle

class Summer_Estelle(Adv):
    a3 = ('bt',0.2)
    conf = {}
    conf['slots.a'] = Candy_Couriers()+Proper_Maintenance()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon.act('c3 s end'), s
        `s2
        `s3
        `s4, x>2
        `s1, x=5
        """
    coab = ['Hunter_Sarisse', 'Renee', 'Tobias']
    share = ['Patia', 'Summer_Luca']

    def init(self):
        self.buff_class = Teambuff if self.condition('buff all team') else Selfbuff
    
    def s2_proc(self, e):
        self.buff_class(e.name,0.15,15).on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
