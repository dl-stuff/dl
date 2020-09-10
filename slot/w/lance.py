from slot import WeaponBase
from slot.w import agito_buffs, LightAgitoWeaponBase


class Chimeratech_Lance(WeaponBase):
    ele = ['all']
    wt = 'lance'
    att = 962
    s3_base = {} #
    a = [('uo', 0.04)]

class Agito2_Gungnir(WeaponBase):
    ele = ['flame']
    wt = 'lance'
    att = 1730
    s3_base = agito_buffs['flame'][1]

class Agito1_Gungnir(WeaponBase):
    ele = ['flame']
    wt = 'lance'
    att = 1575
    s3_base = agito_buffs['flame'][1]

class Agito1_Qinglong_Yanyuedao(WeaponBase):
    ele = ['shadow']
    wt = 'lance'
    att = 1575
    s3_base = agito_buffs['shadow'][1]

class Agito2_Qinglong_Yanyuedao(WeaponBase):
    ele = ['shadow']
    wt = 'lance'
    att = 1730
    s3_base = agito_buffs['shadow'][2]

class Agito1_Rhongomyniad(WeaponBase):
    ele = ['wind']
    wt = 'lance'
    att = 1575
    s3_base = agito_buffs['wind'][1]

class Agito1_Ame_no_Nuhoko(WeaponBase):
    ele = ['water']
    wt = 'lance'
    att = 1575
    s3_base = agito_buffs['water'][1]

class Agito1_Areadbhar(LightAgitoWeaponBase):
    wt = 'lance'
    att = 1575
    s3a = {
        'dmg': 8.28,
        'startup': 0.1,
        'recovery': 3.233, # need confirm
    }

flame = Agito2_Gungnir
water = Agito1_Ame_no_Nuhoko
wind = Agito1_Rhongomyniad
light = Agito1_Areadbhar
shadow = Agito2_Qinglong_Yanyuedao
