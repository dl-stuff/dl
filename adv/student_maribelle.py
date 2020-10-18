from core.advbase import *

def module():
    return Student_Maribelle

class Student_Maribelle(Adv):
    conf = {}
    conf['slots.a'] = [
    'Candy_Couriers',
    'Flash_of_Genius',
    'Moonlight_Party',
    'The_Plaguebringer',
    'Dueling_Dancers'
    ]
    conf['slots.a'] = [
    'Candy_Couriers',
    'Flash_of_Genius',
    'Me_and_My_Bestie',
    'The_Plaguebringer',
    'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon, s=1 or s=4
        `s3, not buff(s3) and x=5
        `s4
        `s2
        `s1, cancel
        `fs,x=5
        """
    conf['coabs'] = ['Gala_Sarisse', 'Serena', 'Yuya']
    conf['share'] = ['Kleimann']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
