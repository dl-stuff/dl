
conf = {
    'xtype': 'ranged',

    'x1.dmg': 0.69,
    'x1.sp': 232,
    'x1.startup': 16/60.0,
    'x1.recovery': 29/60.0,
    'x1.hit': 1,
    'x1.iv': 0,

    'x2.dmg': 0.8,
    'x2.sp': 232,
    'x2.startup': 0,
    'x2.recovery': 42/60.0,
    'x2.hit': 1,
    'x2.iv': 0,

    'x3.dmg': 0.45*2,
    'x3.sp': 348,
    'x3.startup': 0,
    'x3.recovery': 38/60.0,
    'x3.hit': 2,
    'x3.iv': 0,

    'x4.dmg': 1.50,
    'x4.sp': 464,
    'x4.startup': 0,
    'x4.recovery': 67/60.0,
    'x4.hit': 1,
    'x4.iv': 0,

    'x5.dmg': 1.96,
    'x5.sp': 696,
    'x5.startup': 0,
    #'x._recovery': 68/60.0,
    'x5.recovery': 40/60.0,
    'x5.hit': 1,
    'x5.iv': 0,

    'fs.dmg': 0.61*4,
    'fs.sp': 580,
    'fs.charge': 24 / 60.0,
    'fs.startup': 100 / 60.0,
    'fs.recovery': 40 / 60.0,
    'fs.hit': 4,
    'fs.iv': 0,

    'fs.x1.charge': 33 / 60.0, # 9 delay + FS
    'fs.x2.charge': 30 / 60.0, # 6 delay + FS

    'dodge.startup': 36 / 60.0,
    'dodge.recovery': 0 / 60.0,
}

lv2 = {
    'x1.dmg': 82.8 / 100.0,
    'x2.dmg': 96 / 100.0,
    'x3.dmg': 54*2 / 100.0,
    'x4.dmg': 180 / 100.0,
    'x5.dmg': 235.2 / 100.0,
}

# Staff FS Framedata - MsNyara
# Roll: 36
# FS: 24 (Charge) + 42 (FS1) + 22 (FS2) + 22 (FS3) + 14 (FS4) + 40 (Recovery)
# Roll FS: No Interactions Blah.

# C1FS: 16 (C1) + 9 (FS Delay) + FS
# C2FS: 16 (C1) + 29 (C2) +  6 (FS Delay) + FS