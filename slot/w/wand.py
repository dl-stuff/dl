from slot import WeaponBase
from slot.w import agito_buffs, LightAgitoWeaponBase


class Chimeratech_Wand(WeaponBase):
    ele = ['all']
    wt = 'wand'
    att = 1001
    s3_base = {} #
    a = [('uo', 0.04)]

class Agito1_Brisingr(WeaponBase):
    ele = ['flame']
    wt = 'wand'
    att = 1590
    s3 = agito_buffs['flame'][1]

class Agito2_Brisinga(WeaponBase):
    ele = ['flame']
    wt = 'wand'
    att = 1747
    s3 = agito_buffs['flame'][1]

class Agito1_Jiu_Ci(WeaponBase):
    ele = ['shadow']
    wt = 'wand'
    att = 1590
    s3 = agito_buffs['shadow'][1]

class Agito1_Camelot(WeaponBase):
    ele = ['wind']
    wt = 'wand'
    att = 1590
    s3 = agito_buffs['wind'][1]

class Agito1_Omizununo(WeaponBase):
    ele = ['water']
    wt = 'wand'
    att = 1590
    s3 = agito_buffs['water'][1]

class Agito2_Jiu_Ci(WeaponBase):
    ele = ['shadow']
    wt = 'wand'
    att = 1747
    s3 = agito_buffs['shadow'][2]

class Agito1_Brionac(LightAgitoWeaponBase):
    wt = 'wand'
    att = 1590
    s3a = {
        'dmg': 10.84,
        'startup': 0.1,
        'recovery': 1.6667,
    }

flame = Agito2_Brisinga
water = Agito1_Omizununo
wind = Agito1_Camelot
light = Agito1_Brionac
shadow = Agito2_Jiu_Ci