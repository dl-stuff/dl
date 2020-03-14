from slot import WeaponBase
from slot.w import agito_buffs

class HDT1_Conflagration(WeaponBase):
    ele = ['flame']
    wt = 'blade'
    att = 811
    s3 = {
        "dmg"      : 3.54*3   ,
        "sp"       : 7227     ,
        "startup"  : 0.1      ,
        "recovery" : 2.65     ,
        "hit"      : 3        ,
    } # Conflagration Blade
    a = [('k', 0.3, 'vs HMS')]

class HDT2_Blinding_Conflagration(WeaponBase):
    ele = ['flame']
    wt = 'blade'
    att = 1621
    s3 = {
        "dmg"      : 3.54*3   ,
        "sp"       : 7227     ,
        "startup"  : 0.1      ,
        "recovery" : 2.65     ,
        "hit"      : 3        ,
    } # Blinding Blade
    a = []

class HDT1_Torrent(WeaponBase):
    ele = ['water']
    wt = 'blade'
    att = 763
    s3 = {
        "dmg"      : 3.54*3   ,
        "sp"       : 7227     ,
        "startup"  : 0.1      ,
        "recovery" : 2.65     ,
        "hit"      : 3        ,
    } # Torrent Blade
    a = [('k', 0.3, 'vs HBH')]

class HDT2_Ruinous_Torrent(WeaponBase):
    ele = ['water']
    wt = 'blade'
    att = 1527
    s3 = {
        "dmg"      : 3.54*3   ,
        "sp"       : 7227     ,
        "startup"  : 0.1      ,
        "recovery" : 2.65     ,
        "hit"      : 3        ,
    } # Surging Blade
    a = []

class HDT1_Horizon(WeaponBase):
    ele = ['wind']
    wt = 'blade'
    att = 787
    s3 = {
        "dmg"      : 9.57   ,
        "sp"       : 7582   ,
        "startup"  : 0.1    ,
        "recovery" : 2.35   ,
        "hit"      : -1     ,
    } # Horizon Blade
    a = [('k', 0.3, 'vs HMC')]

class HDT2_Endless_Horizon(WeaponBase):
    ele = ['wind']
    wt = 'blade'
    att = 1574
    s3 = {
        "dmg"      : 9.57   ,
        "sp"       : 7582   ,
        "startup"  : 0.1    ,
        "recovery" : 2.35   ,
        "hit"      : -1     ,
    } # Endless Blade
    a = []

class HDT1_Flash(WeaponBase):
    ele = ['light']
    wt = 'blade'
    att = 748
    s3 = {
        "dmg"      : 2.13*5 ,
        "sp"       : 6925   ,
        "startup"  : 0.1    ,
        "recovery" : 2.68   ,
        "hit"      : 5      ,
    } # Flashing Blade
    a = [('k', 0.3, 'vs HZD')]

class HDT2_Brilliant_Flash(WeaponBase):
    ele = ['light']
    wt = 'blade'
    att = 1495
    s3 = {
        "dmg"      : 2.13*5 ,
        "sp"       : 6925   ,
        "startup"  : 0.1    ,
        "recovery" : 2.68   ,
        "hit"      : 5      ,
    } # Brilliant Blade
    a = []

class HDT1_Abyss(WeaponBase):
    ele = ['shadow']
    wt = 'blade'
    att = 811
    s3 = {
        "dmg"      : 2.13*5 ,
        "sp"       : 6925   ,
        "startup"  : 0.1    ,
        "recovery" : 2.68   ,
        "hit"      : 5      ,
    } # Enigmatic Blade
    a = [('k', 0.3, 'vs HJP')]

class HDT2_True_Abyss(WeaponBase):
    ele = ['shadow']
    wt = 'blade'
    att = 1621
    s3 = {
        "dmg"      : 2.13*5 ,
        "sp"       : 6925   ,
        "startup"  : 0.1    ,
        "recovery" : 2.68   ,
        "hit"      : 5      ,
    } # Hellish Blade
    a = []

class Chimeratech_Blade(WeaponBase):
    ele = ['flame', 'shadow']
    wt = 'blade'
    att = 1061
    s3 = {} #
    a = [('uo', 0.04)]

class Agito_Tyrfing(WeaponBase):
    ele = ['flame']
    wt = 'blade'
    att = 1636
    s3 = agito_buffs['flame'][1]

class Agito0UB_Tyrfing(Agito_Tyrfing):
    att = 1051
    s3 = agito_buffs['flame'][0]

class Agito_Qixing_Baodao(WeaponBase):
    ele = ['shadow']
    wt = 'blade'
    att = 1636
    s3 = agito_buffs['shadow'][1]

class Agito0UB_Qixing_Baodao(Agito_Qixing_Baodao):
    att = 1061
    s3 = agito_buffs['shadow'][0]

class UnreleasedAgitoStr_WaterBlade(Agito_Tyrfing):
    ele = ['water']

class UnreleasedAgitoStr_WindBlade(Agito_Tyrfing):
    ele = ['wind']

class UnreleasedAgitoStr_LightBlade(Agito_Tyrfing):
    ele = ['light']

class UnreleasedAgitoSpd_WaterBlade(Agito_Qixing_Baodao):
    ele = ['water']

class UnreleasedAgitoSpd_WindBlade(Agito_Qixing_Baodao):
    ele = ['wind']

class UnreleasedAgitoSpd_LightBlade(Agito_Qixing_Baodao):
    ele = ['light']

flame = Agito_Tyrfing
water = HDT2_Ruinous_Torrent
wind = HDT2_Endless_Horizon
light = HDT2_Brilliant_Flash
shadow = Agito_Qixing_Baodao
