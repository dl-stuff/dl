from slot import WeaponBase
from slot.w import agito_buffs, LightAgitoWeaponBase


class Chimeratech_Staff(WeaponBase):
    ele = ['all']
    wt = 'staff'
    att = 877
    s3_base = {} #
    a = [('uo', 0.04)]

class Agito2_Gjallarhorn(WeaponBase):
    ele = ['flame']
    wt = 'staff'
    att = 1612
    s3_base = agito_buffs['flame'][1]

class Agito1_Goosefoot_Staff(WeaponBase):
    ele = ['shadow']
    wt = 'staff'
    att = 1467
    s3_base = agito_buffs['shadow'][1]

class Agito1_Gjallarhorn(WeaponBase):
    ele = ['flame']
    wt = 'staff'
    att = 1467
    s3_base = agito_buffs['flame'][1]

class Agito1_Avalon(WeaponBase):
    ele = ['wind']
    wt = 'staff'
    att = 1467
    s3_base = agito_buffs['wind'][1]

class Agito1_Kunado(WeaponBase):
    ele = ['water']
    wt = 'staff'
    att = 1467
    s3_base = agito_buffs['water'][1]

class Agito2_Goosefoot_Staff(WeaponBase):
    ele = ['shadow']
    wt = 'staff'
    att = 1612
    s3_base = agito_buffs['shadow'][2]

class Agito1_Del_Frith(LightAgitoWeaponBase):
    wt = 'staff'
    att = 1467
    s3a = {
        'dmg': 7.55,
        'startup': 0.1,
        'recovery': 1.4,
    }

flame = Agito2_Gjallarhorn
water = Agito1_Kunado
wind = Agito1_Avalon
light = Agito1_Del_Frith
shadow = Agito2_Goosefoot_Staff
