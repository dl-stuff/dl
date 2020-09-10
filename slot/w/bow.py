from slot import WeaponBase
from slot.w import agito_buffs, LightAgitoWeaponBase


class Chimeratech_Bow(WeaponBase):
    ele = ['all']
    wt = 'bow'
    att = 961
    s3_base = {} #
    a = [('uo', 0.04)]

class Agito2_Ichaival(WeaponBase):
    ele = ['flame']
    wt = 'bow'
    att = 1629
    s3_base = agito_buffs['flame'][1]

class Agito1_Longshe_Gong(WeaponBase):
    ele = ['shadow']
    wt = 'bow'
    att = 1482
    s3_base = agito_buffs['shadow'][1]

class Agito1_Ydalir(WeaponBase):
    ele = ['flame']
    wt = 'bow'
    att = 1482
    s3_base = agito_buffs['flame'][1]

class Agito1_Failnaught(WeaponBase):
    ele = ['wind']
    wt = 'bow'
    att = 1482
    s3_base = agito_buffs['wind'][1]

class Agito1_Ame_no_Hajiyumi(WeaponBase):
    ele = ['water']
    wt = 'bow'
    att = 1482
    s3_base = agito_buffs['water'][1]

class Agito2_Longshe_Gong(WeaponBase):
    ele = ['shadow']
    wt = 'bow'
    att = 1629
    s3_base = agito_buffs['shadow'][2]

class Agito1_Tathlum(LightAgitoWeaponBase):
    wt = 'bow'
    att = 1482
    s3a = {
        'dmg': 9.49,
        'startup': 0.1,
        'recovery': 2.00,
    }

flame = Agito2_Ichaival
water = Agito1_Ame_no_Hajiyumi
wind = Agito1_Failnaught
light = Agito1_Tathlum
shadow = Agito2_Longshe_Gong