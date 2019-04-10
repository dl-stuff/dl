class Ability(object):
    def __init__(this, name, value, cond=None):
        this.name = name
        this.value = value
        this.cond = cond
        this.mod = []
        if name == 'a' or 'att':
            this.mod = [('att','passive',value, cond)]
        elif name == 's' or 'sd':
            this.mod = [('s','passive',value, cond)]
        elif name == 'cc':
            this.mod = [('crit','chance',value, cond)]
        elif name == 'cd':
            this.mod = [('crit','damage',value, cond)]
        elif name == 'fs':
            this.mod = [('fs','passive',value, cond)]
        elif name == 'bt':
            this.mod = [('buff','time',value, cond)]

        elif name == 'sp':
            if cond != 'fs':
                this.mod = [('sp','passive',value, cond)]

        elif name == 'bk':
            this.mod = [('att','bk',value*0.15, cond)]
        elif name == 'od':
            this.mod = [('att','killer',value*0.45, cond)]

    def oninit(this, adv):
        name = this.name
        cond = this.cond
        value = this.value
        if name == 'sp':
            if cond == 'fs':
                adv.conf.fs.sp *=(1+value)
                Conf.sync(adv.conf.fs)
        elif name == 'lo':
            adv.Buff('lo',value,15)
        elif name == 'bc':
            e = adv.Event('defchain').listener(this.defchain)
            e.adv = adv
        elif name == 'sts':
            adv.Buff('strikerstrength',value*5,-1)
        elif name == 'sls':
            adv.Buff('slayerstrength',value*5,-1)
        elif name == 'dc':
            pass
        elif name == 'prep':
            adv.charge_p("%d%%"%value)
        elif name == 'resist':
            adv.conf.resist = (cond, value)

        j = this.mod
        if type(j) == tuple:
            adv.Modifier(i,*j)
        elif type(j) == list:
            idx = 0
            for k in j:
                adv.Modifier(i+'_%d'%idx,*k)
                idx += 1
        elif type(j) == dict:
            idx = 0
            for k in j:
                adv.Modifier(i+k+'_%d'%idx,*j[k])
                idx += 1


    def defchain(this, e):
        e.adv.Buff('defchain',this.value,15)


    def __repr__(this):
        return str((this.name,this.value,this.cond))

    def __str__(this):
        return str((this.name,this.value,this.cond))

