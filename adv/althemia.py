from core.advbase import *

def module():
    return Althemia

class Althemia(Adv):    
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
        `s2
        `s4
        `s1,buff(s3) and cancel
    """
    conf['coabs'] = ['Gala_Alex','Delphi','Bow']
    conf['share'] = ['Curran']
    

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
