from slot import WeaponBase
from slot.w import agito_buffs, LightAgitoWeaponBase


class Chimeratech_Dagger(WeaponBase):
    ele = ['all']
    wt = 'dagger'
    att = 981
    s3_base = {} #
    a = [('uo', 0.04)]

class Agito2_Hrotti(WeaponBase):
    ele = ['flame']
    wt = 'dagger'
    att = 1662
    s3_base = agito_buffs['flame'][1]

class Agito1_Hrotti(WeaponBase):
    ele = ['flame']
    wt = 'dagger'
    att = 1513
    s3_base = agito_buffs['flame'][1]

class Agito1_Qinghong_Jian(WeaponBase):
    ele = ['shadow']
    wt = 'dagger'
    att = 1513
    s3_base = agito_buffs['shadow'][1]

class Agito2_Qinghong_Jian(WeaponBase):
    ele = ['shadow']
    wt = 'dagger'
    att = 1662
    s3_base = agito_buffs['shadow'][2]

class Agito1_Carnwennan(WeaponBase):
    ele = ['wind']
    wt = 'dagger'
    att = 1513
    s3_base = agito_buffs['wind'][1]

class Agito1_Futsu_no_Mitama(WeaponBase):
    ele = ['water']
    wt = 'dagger'
    att = 1513
    s3_base = agito_buffs['water'][1]

class Agito1_Claiomh_Solais(LightAgitoWeaponBase):
    wt = 'dagger'
    att = 1513
    s3a = {
        'dmg': 6.56,
        'startup': 0.1,
        'recovery': 2.43,
    }

flame = Agito2_Hrotti
water = Agito1_Futsu_no_Mitama
wind = Agito1_Carnwennan
light = Agito1_Claiomh_Solais
shadow = Agito2_Qinghong_Jian
