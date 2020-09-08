from slot import WeaponBase
from slot.w import agito_buffs, LightAgitoWeaponBase


class Chimeratech_Axe(WeaponBase):
    ele = ['all']
    wt = 'axe'
    att = 1051
    s3_base = {} #
    a = [('uo', 0.04)]

class Agito1_Fangtian_Huaji(WeaponBase):
    ele = ['shadow']
    wt = 'axe'
    att = 1621
    s3_base = agito_buffs['shadow'][1]

class Agito2_Fangtian_Huaji(WeaponBase):
    ele = ['shadow']
    wt = 'axe'
    att = 1781
    s3_base = agito_buffs['shadow'][2]

class Agito2_Mjolnir(WeaponBase):
    ele = ['flame']
    wt = 'axe'
    att = 1781
    s3_base = agito_buffs['flame'][1]

class Agito1_Mjolnir(WeaponBase):
    ele = ['flame']
    wt = 'axe'
    att = 1621
    s3_base = agito_buffs['flame'][1]

class Agito1_Marmyadose(WeaponBase):
    ele = ['wind']
    wt = 'axe'
    att = 1621
    s3_base = agito_buffs['wind'][1]

class Agito1_Ohohagari(WeaponBase):
    ele = ['water']
    wt = 'axe'
    att = 1621
    s3_base = agito_buffs['water'][1]

class Agito1_Rog_Mol(LightAgitoWeaponBase):
    wt = 'axe'
    att = 1621
    s3a = {
        'dmg': 11.3,
        'startup': 0.1,
        'recovery': 2.09,
    }

flame = Agito2_Mjolnir
water = Agito1_Ohohagari
wind = Agito1_Marmyadose
light = Agito1_Rog_Mol
shadow = Agito2_Fangtian_Huaji