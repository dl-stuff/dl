from slot import WeaponBase
from slot.w import agito_buffs, LightAgitoWeaponBase


class Chimeratech_Sword(WeaponBase):
    ele = ['all']
    wt = 'sword'
    att = 972
    s3_base = {} #
    a = [('uo', 0.04)]

class Agito2_Nothung(WeaponBase):
    ele = ['flame']
    wt = 'sword'
    att = 1696
    s3_base = agito_buffs['flame'][1]

class Agito1_Yitian_Jian(WeaponBase):
    ele = ['shadow']
    wt = 'sword'
    att = 1544
    s3_base = agito_buffs['shadow'][1]

class Agito1_Nothung(WeaponBase):
    ele = ['flame']
    wt = 'sword'
    att = 1544
    s3_base = agito_buffs['flame'][1]

class Agito1_Excalibur(WeaponBase):
    ele = ['wind']
    wt = 'sword'
    att = 1544
    s3_base = agito_buffs['wind'][1]

class Agito1_Ame_no_Murakumo(WeaponBase):
    ele = ['water']
    wt = 'sword'
    att = 1544
    s3_base = agito_buffs['water'][1]

class Agito2_Yitian_Jian(WeaponBase):
    ele = ['shadow']
    wt = 'sword'
    att = 1696
    s3_base = agito_buffs['shadow'][2]

class Agito1_Caladbolg(LightAgitoWeaponBase):
    wt = 'sword'
    att = 1544
    s3a = {
        'dmg': 9.92,
        'startup': 0.1,
        'recovery': 1.7667,
    }

flame = Agito2_Nothung
water = Agito1_Ame_no_Murakumo
wind = Agito1_Excalibur
light = Agito1_Caladbolg
shadow = Agito2_Yitian_Jian