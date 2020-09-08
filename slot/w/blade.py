from slot import WeaponBase
from slot.w import agito_buffs, LightAgitoWeaponBase


class Chimeratech_Blade(WeaponBase):
    ele = ['all']
    wt = 'blade'
    att = 1061
    s3_base = {} #
    a = [('uo', 0.04)]

class Agito2_Tyrfing(WeaponBase):
    ele = ['flame']
    wt = 'blade'
    att = 1798
    s3 = agito_buffs['flame'][1]

class Agito1_Qixing_Baodao(WeaponBase):
    ele = ['shadow']
    wt = 'blade'
    att = 1636
    s3 = agito_buffs['shadow'][1]

class Agito2_Qixing_Baodao(WeaponBase):
    ele = ['shadow']
    wt = 'blade'
    att = 1798
    s3 = agito_buffs['shadow'][2]

class Agito1_Tyrfing(WeaponBase):
    ele = ['flame']
    wt = 'blade'
    att = 1636
    s3 = agito_buffs['flame'][1]

class Agito1_Arondight(WeaponBase):
    ele = ['wind']
    wt = 'blade'
    att = 1636
    s3 = agito_buffs['wind'][1]

class Agito1_Ame_no_Habakiri(WeaponBase):
    ele = ['water']
    wt = 'blade'
    att = 1636
    s3 = agito_buffs['water'][1]

class Agito1_Fragarach(LightAgitoWeaponBase):
    wt = 'blade'
    att = 1636
    s3a = {
        'dmg': 8.52,
        'startup': 0.1,
        'recovery': 2.2,
    }

flame = Agito2_Tyrfing
water = Agito1_Ame_no_Habakiri
wind = Agito1_Arondight
light = Agito1_Fragarach
shadow = Agito2_Qixing_Baodao
