from core.advbase import Adv

class Addis(Adv):
    conf = {}    
    conf['mbleed'] = True

class Addis_RNG(Adv):
    conf = {}    
    conf['mbleed'] = False

variants = {
    None: Addis,
    'rng': Addis_RNG
}