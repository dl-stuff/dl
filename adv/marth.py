from core.advbase import *

def module():
    return Marth

class Marth(Adv):
    comment = 'last boost once at start (team DPS not considered)'

    conf = {}
    conf['slots.a'] = [
    'The_Shining_Overlord',
    'Flash_of_Genius',
    'Me_and_My_Bestie',
    'Chariot_Drift',
    'Dueling_Dancers'
    ]
    conf['acl'] = """
        queue not buff(s3)
        `s3;s1;s2;fs,x=2;s4,fsc
        end
        `dragon,s=2
        queue prep and afflics.burn.get()
        `s2;s4
        end
        queue prep and not afflics.burn.get()
        `s1;s2;s4
        end
        `s2, afflics.burn.get()
        `s4, cancel
        `s1, fsc and not energy()=5
        `fs, x=3
        """
    conf['coabs.base'] = ['Yuya', 'Wand', 'Joe']
    conf['coabs.burn'] = ['Halloween_Mym', 'Wand', 'Yuya']
    conf['share'] = ['Gala_Mym']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
