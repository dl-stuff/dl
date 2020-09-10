from slot import WeaponBase
from slot.w import agito_buffs, LightAgitoWeaponBase

class HDT1_Crimson(WeaponBase):
    ele = ['flame']
    wt = 'sword'
    att = 765
    s3 = {
        "dmg"      : 5*1.65   ,
        "sp"       : 6847     ,
        "startup"  : 0.1      ,
        "recovery" : 3.1      ,
        "hit"      : 5        ,
    } # Crimson Storm
    a = [('k', 0.3, 'vs HMS')]

class HDT2_Absolute_Crimson(WeaponBase):
    ele = ['flame']
    wt = 'sword'
    att = 1530
    s3 = {
        "dmg"      : 5*1.65   ,
        "sp"       : 6847     ,
        "startup"  : 0.1      ,
        "recovery" : 3.1      ,
        "hit"      : 5        ,
    } # Infinite Crimson
    a = []

class HDT1_Aqua(WeaponBase):
    ele = ['water']
    wt = 'sword'
    att = 765
    s3 = {
        "dmg"      : 3*2.48   ,
        "sp"       : 6418     ,
        "startup"  : 0.1      ,
        "recovery" : 1.9      ,
        "hit"      : 3        ,
    } # Aqua Storm
    a = [('k', 0.3, 'vs HBH')]

class HDT2_Absolute_Aqua(WeaponBase):
    ele = ['water']
    wt = 'sword'
    att = 1530
    s3 = {
        "dmg"      : 3*2.48   ,
        "sp"       : 6418     ,
        "startup"  : 0.1      ,
        "recovery" : 1.9      ,
        "hit"      : 3        ,
    } # Infinite Aqua
    a = []

class HDT1_Tempest(WeaponBase):
    ele = ['wind']
    wt = 'sword'
    att = 705
    s3 = {
        "dmg"      : 3*2.48   ,
        "sp"       : 6418     ,
        "startup"  : 0.1      ,
        "recovery" : 1.9      ,
        "hit"      : 3        ,
    } # Tempest Storm
    a = [('k', 0.3, 'vs HMC')]

class HDT2_Absolute_Tempest(WeaponBase):
    ele = ['wind']
    wt = 'sword'
    att = 1411
    s3 = {
        "dmg"      : 3*2.48   ,
        "sp"       : 6418     ,
        "startup"  : 0.1      ,
        "recovery" : 1.9      ,
        "hit"      : 3        ,
    } # Infinite Tempest
    a = []

class HDT1_Lightning(WeaponBase):
    ele = ['light']
    wt = 'sword'
    att = 743
    s3 = {
        "dmg"      : 3*2.48   ,
        "sp"       : 6418     ,
        "startup"  : 0.1      ,
        "recovery" : 1.9      ,
        "hit"      : 3        ,
    } # Lightning Storm
    a = [('k', 0.3, 'vs HZD')]

class HDT2_Absolute_Lightning(WeaponBase):
    ele = ['light']
    wt = 'sword'
    att = 1485
    s3 = {
        "dmg"      : 3*2.48   ,
        "sp"       : 6418     ,
        "startup"  : 0.1      ,
        "recovery" : 1.9      ,
        "hit"      : 3        ,
    } # Infinite Lightning
    a = []

class HDT1_Hex(WeaponBase):
    ele = ['shadow']
    wt = 'sword'
    att = 743
    s3 = {
        "dmg"      : 5*1.65   ,
        "sp"       : 6163     ,
        "startup"  : 0.1      ,
        "recovery" : 3.1      ,
        "hit"      : 5        ,
    } # Hexing Storm
    a = [('k', 0.3, 'vs HJP')]

class HDT2_Absolute_Hex(WeaponBase):
    ele = ['shadow']
    wt = 'sword'
    att = 1485
    s3 = {
        "dmg"      : 5*1.65   ,
        "sp"       : 6163     ,
        "startup"  : 0.1      ,
        "recovery" : 3.1      ,
        "hit"      : 5        ,
    } # Infinite Hexes
    a = []

class Chimeratech_Sword(WeaponBase):
    ele = ['flame', 'shadow', 'wind']
    wt = 'sword'
    att = 972
    s3 = {} #
    a = [('uo', 0.04)]

class Agito2_Nothung(WeaponBase):
    ele = ['flame']
    wt = 'sword'
    att = 1696
    s3 = agito_buffs['flame'][1]

class Agito1_Yitian_Jian(WeaponBase):
    ele = ['shadow']
    wt = 'sword'
    att = 1544
    s3 = agito_buffs['shadow'][1]

class Agito1_Nothung(WeaponBase):
    ele = ['flame']
    wt = 'sword'
    att = 1544
    s3 = agito_buffs['flame'][1]

class Agito1_Excalibur(WeaponBase):
    ele = ['wind']
    wt = 'sword'
    att = 1544
    s3 = agito_buffs['wind'][1]

class Agito1_Ame_no_Murakumo(WeaponBase):
    ele = ['water']
    wt = 'sword'
    att = 1544
    s3 = agito_buffs['water'][1]

class Agito2_Yitian_Jian(WeaponBase):
    ele = ['shadow']
    wt = 'sword'
    att = 1696
    s3 = agito_buffs['shadow'][2]

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