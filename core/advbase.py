import operator
import sys
import random
from functools import reduce
from itertools import product, chain
from collections import OrderedDict

# from core import *
from core.config import Conf
from core.timeline import *
from core.log import *
from core.afflic import *
from core.modifier import *
from core.dummy import Dummy, dummy_function
from core.condition import Condition
from core.slots import Slots
import core.acl
import conf as globalconf
from ctypes import c_float
from math import ceil

class Skill(object):
    _static = Static({
        's_prev': '<nop>',
        'first_x_after_s': 0,
        'silence': 0,
        'current_s': {}
    })
    charged = 0
    sp = 0
    silence_duration = 1.9
    name = '_Skill'

    def __init__(self, name=None, acts=None):
        self.charged = 0
        self.name = name

        self.act_dict = acts or {}
        self.act_base = None

        self._static.silence = 0
        self.silence_end_timer = Timer(self.cb_silence_end)
        self.silence_end_event = Event('silence_end')
        self.skill_charged = Event('{}_charged'.format(self.name))

        self.enable_phase_up = None

    def add_action(self, group, act):
        self.act_dict[group] = act
        if group == 'default':
            self.act_base = act
        if isinstance(group, int):
            self.enable_phase_up = True

    def set_enabled(self, enabled):
        for ac in self.act_dict.values():
            ac.enabled = enabled

    @property
    def phase(self):
        return self._static.current_s[self.name]

    @property
    def ac(self):
        try:
            return self.act_dict[self._static.current_s[self.name]]
        except KeyError:
            return self.act_base

    @property
    def sp(self):
        return self.ac.conf.sp

    @property
    def owner(self):
        return self.act_base.conf['owner'] or None

    def phase_up(self):
        p_max = self.act_base.conf.p_max
        if p_max:
            cur_s = self._static.current_s[self.name]
            cur_s = (cur_s+1)%p_max
            self._static.current_s[self.name] = cur_s

    def __call__(self, *args):
        if not self.check():
            return False
        if not self.ac():
            return False
        self.enable_phase_up and self.phase_up()
        return self.cast()

    def charge(self, sp):
        if not self.ac.enabled:
            return
        self.charged = max(min(self.sp, self.charged + sp), 0)
        if self.charged >= self.sp:
            self.skill_charged()

    def cb_silence_end(self, e):
        if loglevel >= 2:
            log('silence', 'end')
        self._static.silence = 0
        self.silence_end_event()

    def check(self):
        if self._static.silence == 1 or not self.ac.enabled or self.sp == 0:
            return False
        return self.charged >= self.sp

    def cast(self):
        self.charged -= self.sp
        self._static.s_prev = self.name
        # Even if animation is shorter than 1.9, you can't cast next skill before 1.9
        self.silence_end_timer.on(self.silence_duration)
        self._static.silence = 1
        if loglevel >= 2:
            log('silence', 'start')
        return 1

    def autocharge_init(self, sp, iv=1):
        if callable(sp):
            self.autocharge_timer = Timer(sp, iv, 1)
        else:
            if sp < 1:
                sp = int(sp * self.sp)
            def autocharge(t):
                if self.charged < self.sp:
                    self.charge(sp)
                    log('sp', self.name+'_autocharge', int(sp))
            self.autocharge_timer = Timer(autocharge, iv, 1)
        return self.autocharge_timer


class Action(object):
    _static = Static({
        'prev': 0,
        'doing': 0,
        'spd_func': 0,
        'c_spd_func': 0,
    })
    OFF = -2
    STARTUP = -1
    DOING = 0
    RECOVERY = 1

    name = '_Action'
    index = 0
    recover_start = 0
    startup_start = 0
    status = -2
    idle = 0

    class Nop(object):
        name = 'nop'
        index = 0
        status = -2
        idle = 1
        has_delayed = 0

    nop = Nop()

    def __init__(self, name=None, conf=None, act=None):  ## can't change name after self
        if name != None:
            if type(name) == tuple:
                self.name = name[0]
                self.index = name[1]
            else:
                self.name = name
                self.index = 0
            self.atype = self.name

        self.conf = conf

        if act != None:
            self.act = act

        if not self._static.spd_func:
            self._static.spd_func = self.nospeed
        if not self._static.c_spd_func:
            self._static.c_spd_func = self.nospeed
        if not self._static.doing:
            self._static.doing = self.nop
        if not self._static.prev:
            self._static.prev = self.nop

        self.cancel_by = []
        self.interrupt_by = []

        self.startup_timer = Timer(self._cb_acting)
        self.recovery_timer = Timer(self._cb_act_end)
        self.idle_event = Event('idle')
        self.act_event = Event(self.name)

        self.enabled = True
        self.delayed = set()
        # ?????
        # self.rt_name = self.name
        # self.tap, self.o_tap = self.rt_tap, self.tap

    def __call__(self):
        return self.tap()

    def getdoing(self):
        return self._static.doing

    def _setdoing(self):
        self._static.doing = self

    def getprev(self):
        return self._static.prev

    def _setprev(self):
        self._static.prev = self._static.doing

    def rt_tap(self):
        if self.rt_name != self.name:
            if self.atype == self.rt_name:
                self.atype = self.name
            self.rt_name = self.name
            self.act_event = Event(self.name)
        return self.o_tap()


    @property
    def _startup(self):
        return self.conf.startup

    @property
    def _recovery(self):
        return self.conf.recovery

    def getrecovery(self):
        # Lathna/Ramona spaget
        if 'recovery_nospd' in self.conf:
            return self._recovery / self.speed() + self.conf['recovery_nospd']
        return self._recovery / self.speed()

    def getstartup(self):
        return self._startup / self.speed()

    def nospeed(self):
        return 1

    def speed(self):
        return self._static.spd_func()

    def _cb_acting(self, e):
        if self.getdoing() == self:
            self.status = 0
            self._act(1)
            self.status = Action.RECOVERY
            self.recover_start = now()
            self.recovery_timer.on(self.getrecovery())

    def _cb_act_end(self, e):
        if self.getdoing() == self:
            if loglevel >= 2:
                log('ac_end', self.name)
            self.status = Action.OFF
            self._setprev()  # turn self from doing to prev
            self._static.doing = self.nop
            self.idle_event()

    def _act(self, partidx):
        self.idx = partidx
        if loglevel >= 2:
            log('act', self.name)
        self.act(self)

    def act(self, action):
        self.act_event()

    def add_delayed(self, mt):
        self.delayed.add(mt)

    def clear_delayed(self):
        count = 0
        for mt in self.delayed:
            if mt.online:
                count += 1
            mt.off()
        self.delayed = set()
        return count

    @property
    def has_delayed(self):
        return len([mt for mt in self.delayed if mt.online and mt.timing > now()])

    def tap(self):
        doing = self._static.doing

        if doing.idle:
            if loglevel >= 2:
                log('tap', self.name, self.atype, f'idle {doing.status}')
        else:
            if loglevel >= 2:
                log('tap', self.name, self.atype, f'doing {doing.name}:{doing.status}')

        if doing == self:  # self is doing
            return 0

        # if doing.idle # idle
        #    pass
        if not doing.idle:  # doing != self
            if doing.status == Action.STARTUP:  # try to interrupt an action
                if self.atype in doing.interrupt_by:  # can interrupt action
                    doing.startup_timer.off()
                    logargs = ['interrupt', doing.name, f'by {self.name}']
                    delta = now() - doing.startup_start
                    if delta > 0:
                        logargs.append(f'after {delta:.2f}s')
                    log(*logargs)
                else:
                    return 0
            elif doing.status == Action.RECOVERY:  # try to cancel an action
                if self.atype in doing.cancel_by:  # can interrupt action
                    doing.recovery_timer.off()
                    count = doing.clear_delayed()
                    delta = now() - doing.recover_start
                    logargs = ['cancel', doing.name, f'by {self.name}']
                    if delta > 0:
                        logargs.append(f'after {delta:.2f}s')
                    if count > 0:
                        logargs.append(f'lost {count} hit{"s" if count > 1 else ""}')
                    log(*logargs)
                else:
                    return 0
            elif doing.status == 0:
                raise Exception(f'Illegal action {doing} -> {self}')
            self._setprev()
        self.delayed = set()
        self.status = Action.STARTUP
        self.startup_start = now()
        self.startup_timer.on(self.getstartup())
        self._setdoing()
        if now() <= 3:
            log('debug', 'tap', 'startup', self.getstartup())
        return 1


class X(Action):
    def __init__(self, name, conf, act=None):
        parts = name.split('_')
        index = int(parts[0][1:])
        super().__init__((name, index), conf, act)
        self.base = parts[0]
        self.group = 'default' if len(parts) == 1 else parts[1]
        self.atype = 'x'
        self.interrupt_by = ['fs', 's', 'dodge']
        self.cancel_by = ['fs', 's', 'dodge']

        self.act_event = Event('x')
        self.act_event.name = self.name
        self.act_event.base = self.base
        self.act_event.index = self.index
        self.act_event.group = self.group

        self.rt_name = self.name
        self.tap, self.o_tap = self.rt_tap, self.tap

    def rt_tap(self):
        if self.rt_name != self.name:
            if self.atype == self.rt_name:
                self.atype = self.name
            self.rt_name = self.name
            self.act_event.name = self.name
        return self.o_tap()


class Fs(Action):
    def __init__(self, name, conf, act=None):
        super().__init__(name, conf, act)
        parts = name.split('_')
        self.act_event = Event('fs')
        self.act_event.name = self.name
        self.act_event.base = parts[0]
        self.act_event.group = 'default'
        self.act_event.level = 0
        if len(parts) >= 2:
            self.act_event.group = parts[1]
        if len(parts[0]) > 2:
            try:
                self.act_event.level = int(parts[0][2:])
            except ValueError:
                pass
        self.atype = 'fs'
        self.interrupt_by = ['s']
        self.cancel_by = ['s', 'dodge']

    @property
    def _charge(self):
        return self.conf.charge

    def charge_speed(self):
        return self._static.c_spd_func()

    def getstartup(self):
        return (self._charge / self.charge_speed()) + (self._startup / self.speed())


class Fs_group(object):
    def __init__(self, name, conf, act=None):
        self.enabled = True
        self.conf = conf
        self.actions = {'default': Fs(name, self.conf, act)}
        for xn, xnconf in conf.find(r'^x\d+$'):
            self.actions[xn] = Fs(name, self.conf+xnconf, act)
        if conf['s']:
            fs_s = Fs(name, self.conf+conf['s'], act)
            for n in range(1, 5):
                sn = f's{n}'
                self.actions[sn] = fs_s
        if conf['dodge']:
            self.actions['dodge'] = Fs(name, self.conf+conf['dodge'], act)

    def set_enabled(self, enabled):
        for fs in self.actions.values():
            fs.enabled = enabled
        self.enabled = enabled

    def __call__(self, before):
        if not self.enabled:
            return False
        try:
            return self.actions[before]()
        except KeyError:
            return self.actions['default']()


class S(Action):
    def __init__(self, name, conf, act=None):
        super().__init__(name, conf, act)
        self.atype = 's'
        self.interrupt_by = []
        self.cancel_by = []

        parts = name.split('_')
        self.base = parts[0]
        self.group = 'default'
        self.phase = None
        if len(parts) >= 2:
            self.group = parts[1]

        self.act_event = Event('s')
        self.act_event.name = self.name
        self.act_event.base = self.base
        self.act_event.group = self.group
        self.act_event.phase = 0


class Dodge(Action):
    def __init__(self, name, conf, act=None):
        Action.__init__(self, name, conf, act)
        self.atype = 'dodge'
        self.cancel_by = ['fs', 's']

        self.act_event = Event('dodge')
        self.act_event.name = self.name

    def getstartup(self):
        return self._startup

    def getrecovery(self):
        return self._recovery


class Adv(object):
    Timer = Timer
    Event = Event
    Listener = Listener

    name = None
    _acl_default = None
    _acl_dragonbattle = core.acl.build_acl('`dragon')
    _acl = None

    def dmg_proc(self, name, amount):
        pass

    """
    New before/proc system:
    x/fs/s events will try to call <name>_before before everything, and <name>_proc at each hitattr

    Examples:
    Albert FS:
        fs_proc is called when he uses base fs
        fs2_proc is called when he uses alt fs2

    Addis s1:
        s1_hit1 is called after the 1st s1 hit when s2 buff is not active
        s1_enhanced_hit1 after the 1st s1 hit is called when s2 buff is active
        s1_proc is called after the final (4th) hit

    Mitsuba:
        x_proc is called when base dagger combo
        x_tempura_proc is called when tempura combo
    """

    def d_coabs(self):
        pass

    def d_slots(self):
        pass

    def d_skillshare(self):
        pass

    def prerun(self):
        pass

    @staticmethod
    def prerun_skillshare(adv, dst):
        pass

    comment = ''
    conf = {}
    a1 = None
    a2 = None
    a3 = None

    skill_default = {'dmg': 0, 'hit': 0, 'recovery': 1.8, 'sp': 0, 'startup': 0.1}
    conf_default = {
        # Latency represents the human response time, between when an event
        # triggers a "think" event, and when the human actually triggers
        # the input.  Right now it's set to zero, which means "perfect"
        # response time (which is unattainable in reality.)
        'latency.x': 0,
        'latency.sp': 0,
        'latency.default': 0,
        'latency.idle': 0,

        's1': skill_default,
        's2': skill_default,
        's3': skill_default,
        's4': skill_default,

        'dodge.startup': 0.63333,
        'dodge.recovery': 0,

        'acl': '`s1;`s2;`s3',

        'attenuation.hits': 1,
        'attenuation.delay': 0.25,
    }

    def damage_sources_check(self, name, conf):
        if conf['attr'] and any(('dmg' in attr for attr in conf['attr'] if isinstance(attr, dict))):
            self.damage_sources.add(name)
        if conf.get('energizable'):
            self.energy.extra_tensionable.add(name)

    def doconfig(self):
        # set act
        self.action = Action()
        self.action._static.spd_func = self.speed
        self.action._static.c_spd_func = self.c_speed
        # set buff
        self.base_buff = Buff()
        self.all_buffs = []
        self.base_buff._static.all_buffs = self.all_buffs
        self.base_buff._static.adv = self
        self.buff = ActiveBuffDict()
        # set modifier
        self.modifier = Modifier(0, 0, 0, 0)
        self.all_modifiers = ModifierDict()
        self.modifier._static.all_modifiers = self.all_modifiers
        self.modifier._static.g_condition = self.condition

        # init actions
        for xn, xconf in self.conf.find(r'^x\d+(_[A-Za-z0-9]+)?$'):
            a_x = X(xn, self.conf[xn])
            if xn != a_x.base and self.conf[a_x.base]:
                a_x.conf.update(self.conf[a_x.base], rebase=True)
            self.a_x_dict[a_x.group][a_x.index] = a_x
            self.damage_sources_check(xn, xconf)
        self.a_x_dict = dict(self.a_x_dict)
        for group, actions in self.a_x_dict.items():
            gxmax = f'{group}.x_max'
            if not self.conf[gxmax]:
                self.conf[gxmax] = max(actions.keys())
        self.current_x = 'default'
        self.deferred_x = None

        for name, fs_conf in self.conf.find(r'^fs\d*(_[A-Za-z0-9]+)?$'):
            try:
                base = name.split('_')[0]
                if name != base and self.conf[base]:
                    fs_conf.update(self.conf[base], rebase=True)
            except KeyError:
                pass
            self.a_fs_dict[name] = Fs_group(name, fs_conf)
            self.damage_sources_check(name, fs_conf)
        if 'fs1' in self.a_fs_dict:
            self.a_fs_dict['fs'].enabled = False
        self.current_fs = None
        self.alt_fs_buff = None

        self.a_fsf = Fs('fsf', self.conf.fsf)
        self.a_fsf.act_event = Event('none')

        self.a_dodge = Dodge('dodge', self.conf.dodge)

        # # skill init
        # self.s1 = Skill('s1', self.conf.s1)
        # self.s2 = Skill('s2', self.conf.s2)
        # self.s3 = Skill('s3', self.conf.s3)
        # self.s4 = Skill('s4', self.conf.s4)

        # if self.conf.xtype == 'ranged':
        #     self.l_x = self.l_range_x
        #     self.l_fs = self.l_range_fs
        # elif self.conf.xtype == 'melee':
        #     self.l_x = self.l_melee_x
        #     self.l_fs = self.l_melee_fs

        # set cmd
        self.fsf = self.a_fsf
        self.dodge = self.a_dodge

        if self.conf['auto_fsf']:
            self.cb_think = self._cb_think_fsf
        else:
            self.cb_think = self._cb_think

        # try:
        #     self.x5ex = X(('x5ex', 5), self.conf.x5ex)
        #     self.x5ex.atype = 'x'
        #     self.x5ex.interrupt_by = ['fs', 's', 'dodge']
        #     self.x5ex.cancel_by = ['fs', 's', 'dodge']
        #     self.x4.cancel_by.append('x')
        # except:
        #     pass

        self.hits = 0
        self.last_c = 0
        self.ctime_override = 0

        self.hp = 100
        self.hp_event = Event('hp')
        self.dragonform = None

        from module.tension import Energy, Inspiration
        self.energy = Energy()
        self.inspiration = Inspiration()
        self.tension = [self.energy, self.inspiration]
        self.sab = []
        self.extra_actmods = []

        self.disable_echo()
        self.bleed = None

    @property
    def ctime(self):
        # base ctime is 2
        return self.ctime_override or self.mod('ctime') + 1

    def actmod_on(self, e):
        do_sab = True
        do_tension = e.name.startswith('s') or e.name == 'ds'
        if do_tension:
            for t in self.tension:
                t.on(e)
        if do_sab:
            for b in self.sab:
                b.act_on(e)

    def actmods(self, name):
        mods = [m for m in self.extra_actmods if name == m.mod_name]
        for t in chain(self.tension, self.sab):
            if name in t.active:
                mods.append(t.modifier)
        if name[0] == 'd':
            mods.extend(self.dragonform.shift_mods)
        # log('actmods', name, str(mods))
        return mods

    def actmod_off(self, e):
        do_sab = True
        do_tension = e.name.startswith('s') or e.name == 'ds'
        if do_tension:
            for t in self.tension:
                t.off(e)
        if do_sab:
            for b in self.sab:
                b.act_off(e)

    def l_set_hp(self, e):
        try:
            self.add_hp(e.delta)
        except AttributeError:
            self.set_hp(e.hp)

    def add_hp(self, delta):
        self.set_hp(self.hp+delta)

    def set_hp(self, hp):
        if self.conf['flask_env'] and 'hp' in self.conf:
            hp = self.conf['hp']
        old_hp = self.hp
        hp = round(hp*10)/10
        self.hp = max(min(hp, 100), 0)
        if self.hp != old_hp:
            delta = self.hp-old_hp
            if self.hp == 0:
                log('hp', f'=1', f'{delta/100:.2%}')
            else:
                log('hp', f'{self.hp/100:.2%}', f'{delta/100:.2%}')
            self.condition.hp_cond_set(self.hp)
            self.hp_event.hp = self.hp
            self.hp_event.delta = delta
            self.hp_event()

    def afflic_condition(self):
        if 'afflict_res' in self.conf:
            res_conf = self.conf.afflict_res
            for afflic in AFFLICT_LIST:
                if afflic in res_conf and 0 <= res_conf[afflic] <= 100:
                    if self.condition('{} {} res'.format(res_conf[afflic], afflic)):
                        vars(self.afflics)[afflic].resist = res_conf[afflic]
                    else:
                        vars(self.afflics)[afflic].resist = 100

    def sim_affliction(self):
        if 'sim_afflict' in self.conf:
            for aff_type in AFFLICT_LIST:
                aff = vars(self.afflics)[aff_type]
                if self.conf.sim_afflict[aff_type]:
                    aff.get_override = min(self.conf.sim_afflict[aff_type], 1.0)
                    self.sim_afflict.add(aff_type)

    def sim_buffbot(self):
        if 'sim_buffbot' in self.conf:
            if 'def_down' in self.conf.sim_buffbot:
                value = self.conf.sim_buffbot.def_down
                if self.condition('boss def {:+.0%}'.format(value)):
                    buff = self.Selfbuff('simulated_def', value, -1, mtype='def')
                    buff.chance = 1
                    buff.val = value
                    buff.on()
            if 'str_buff' in self.conf.sim_buffbot:
                if self.condition('team str {:+.0%}'.format(self.conf.sim_buffbot.str_buff)):
                    self.Selfbuff('simulated_att', self.conf.sim_buffbot.str_buff, -1).on()
            if 'critr' in self.conf.sim_buffbot:
                if self.condition('team crit rate {:+.0%}'.format(self.conf.sim_buffbot.critr)):
                    self.Selfbuff('simulated_crit_rate', self.conf.sim_buffbot.critr, -1, 'crit', 'chance').on()
            if 'critd' in self.conf.sim_buffbot:
                if self.condition('team crit dmg {:+.0%}'.format(self.conf.sim_buffbot.critd)):
                    self.Selfbuff('simulated_crit_dmg', self.conf.sim_buffbot.critd, -1, 'crit', 'damage').on()
            if 'echo' in self.conf.sim_buffbot:
                if self.condition('echo att {:g}'.format(self.conf.sim_buffbot.echo)):
                    self.enable_echo(fixed_att=self.conf.sim_buffbot.echo)
            if 'doublebuff_interval' in self.conf.sim_buffbot:
                interval = round(self.conf.sim_buffbot.doublebuff_interval, 2)
                if self.condition('team doublebuff every {:.2f} sec'.format(interval)):
                    Event('defchain').on()
                    Timer(lambda t: Event('defchain').on(), interval, True).on()

    def config_slots(self):
        if self.conf['classbane'] == 'HDT':
            self.conf.c.a.append(['k_HDT', 0.3])
        if not self.conf['flask_env']:
            self.d_slots()
        self.slots.set_slots(self.conf.slots)

    def pre_conf(self, equip_key=None):
        self.conf = Conf(self.conf_default)
        self.conf.update(globalconf.get_adv(self.name))
        self.conf.update(self.conf_base)
        equip = globalconf.load_equip_json(self.name)
        equip_d = equip.get(str(int(self.duration)))
        if not equip_d:
            equip_d = equip.get('180')
        if equip_d:
            if equip_key is None:
                equip_key = equip_d.get('pref', 'base')
                self.equip_key = equip_key
            elif equip_key == 'affliction':
                from core.simulate import ELE_AFFLICT
                self.equip_key = 'affliction'
                equip_key = ELE_AFFLICT[self.conf.c.ele]
            if equip_key in equip_d:
                self.conf.update(equip_d[equip_key])
                self.equip_key = self.equip_key or equip_key
            elif 'base' in equip_d:
                self.conf.update(equip_d['base'])
        self.conf.update(self.conf_init)
        return equip_d

    def default_slot(self):
        self.slots = Slots(self.name, self.conf.c, self.sim_afflict, bool(self.conf['flask_env']))
        # from conf import slot_common
        # self.cmnslots = slot.Slots()
        # self.cmnslots.c.att = self.conf.c.att
        # self.cmnslots.c.wt = self.conf.c.wt
        # self.cmnslots.c.ele = self.conf.c.ele
        # self.cmnslots.c.name = self.name
        # self.slot_common = slot_common.set
        # self.slot_common(self.cmnslots)
        # self.slots = self.cmnslots

    def __init__(self, conf=None, duration=180, cond=None, equip_key=None):
        if not self.name:
            self.name = self.__class__.__name__

        self.Event = Event
        self.Buff = Buff
        self.Debuff = Debuff
        self.Selfbuff = Selfbuff
        self.Teambuff = Teambuff
        self.Modifier = Modifier
        self.Conf = Conf

        self.conf_base = Conf(self.conf or {})
        self.conf_init = Conf(conf or {})
        self.ctx = Ctx().on()
        self.condition = Condition(cond)
        self.duration = duration

        self.damage_sources = set()
        self.Modifier._static.damage_sources = self.damage_sources

        self.equip_key = None
        equip = self.pre_conf(equip_key=equip_key)

        # set afflic
        self.afflics = Afflics()
        self.sim_afflict = set()
        self.afflic_condition()
        self.sim_affliction()

        self.default_slot()

        self.crit_mod = self.solid_crit_mod
        # self.crit_mod = self.rand_crit_mod

        self.Skill = Skill()

        self.a_x_dict = defaultdict(lambda: {})
        self.a_fs_dict = {}
        self.a_s_dict = {f's{n}': Skill(f's{n}') for n in range(1, 5)}

        # self.classconf = self.conf
        # self.init()

        # self.ctx.off()
        self._acl = None

        self.stats = []

    def dmg_mod(self, name):
        mod = 1
        scope = name.split('_')
        if scope[0] == 'o':
            scope = scope[1]
        else:
            scope = scope[0]
        if name.startswith('dx') or name == 'dshift':
            scope = 'x'
        elif name == 'ds':
            scope = 's'

        if scope[0] == 's':
            try:
                mod = 1 if name == 'ds' or self.a_s_dict[scope].owner is None else self.skill_share_att
            except:
                pass
            return mod * self.mod('s')
        elif scope[0:2] == 'fs':
            return mod * self.mod('fs')
        elif scope[0] == 'x':
            return mod * self.mod('x')
        else:
            return mod

    # @staticmethod
    # def mod_mult(a, b):
    #     return a * (1 + b)

    def mod(self, mtype, operator=None, initial=1):
        return self.all_modifiers.mod(mtype, operator=operator, initial=initial)
        # operator = operator or Adv.mod_mult
        # return reduce(operator, [self.sub_mod(mtype, order) for order in self.all_modifiers[mtype].keys()], initial)

    def sub_mod(self, mtype, morder):
        return self.all_modifiers.sub_mod(mtype, morder)
    # def sub_mod(self, mtype, morder):
    #     mod_sum = sum([modifier.get() for modifier in self.all_modifiers[mtype][morder]])
    #     if morder == 'buff':
    #         mod_sum = min(mod_sum, 2.00)
    #     return mod_sum

    def speed(self, target=None):
        if target is None:
            return min(1+self.sub_mod('spd', 'passive'), 1.50)
        else:
            return min(1+self.sub_mod('spd', 'passive')+self.sub_mod('spd', target), 1.50)

    def c_speed(self):
        return min(1+self.sub_mod('cspd', 'passive'), 1.50)

    def enable_echo(self, mod=None, fixed_att=None):
        self.echo = 2
        self.echo_att = fixed_att or (mod * self.base_att * self.mod('att'))
        log('debug', 'echo_att', self.echo_att)

    def disable_echo(self):
        self.echo = 1
        self.echo_att = 0

    def dmg_formula_echo(self, coef):
        # so 5/3(Bonus Damage amount)/EnemyDef +/- 5%
        armor = 10 * self.def_mod()
        return 5/3 * (self.echo_att * coef) / armor

    def crit_mod(self):
        return 1

    def combine_crit_mods(self):
        m = {'chance': 0, 'damage': 0}
        for order, modifiers in self.all_modifiers['crit'].items():
            for modifier in modifiers:
                if order in m:
                    m[order] += modifier.get()
                else:
                    raise ValueError(f"Invalid crit mod order {order}")

        rate_list = self.build_rates()
        for mask in product(*[[0, 1]] * len(rate_list)):
            p = 1.0
            modifiers = defaultdict(lambda: set())
            for i, on in enumerate(mask):
                cond = rate_list[i]
                cond_name = cond[0]
                cond_p = cond[1]
                if on:
                    p *= cond_p
                    for order, mods in self.all_modifiers[f'{cond_name}_crit'].items():
                        for mod in mods:
                            modifiers[order].add(mod)
                else:
                    p *= 1 - cond_p
            # total += p * reduce(operator.mul, [1 + sum([mod.get() for mod in order]) for order in modifiers.values()], 1.0)
            for order, values in modifiers.items():
                m[order] += p * sum([mod.get() for mod in values])

        chance = min(m['chance'], 1)
        cdmg = m['damage'] + 1.7

        return chance, cdmg

    def solid_crit_mod(self, name=None):
        chance, cdmg = self.combine_crit_mods()
        average = chance * (cdmg - 1) + 1
        return average

    def rand_crit_mod(self, name=None):
        chance, cdmg = self.combine_crit_mods()
        r = random.random()
        if r < chance:
            return cdmg
        else:
            return 1

    def att_mod(self, name=None):
        att = self.mod('att')
        cc = self.crit_mod(name)
        k = self.killer_mod(name)
        # if name == 's1_ddrive':
        #     print(dict(self.all_modifiers['att']))
        #     exit()
        return cc * att * k
    
    def build_rates(self, as_list=True):
        rates = {}
        for afflic in AFFLICT_LIST:
            rate = vars(self.afflics)[afflic].get()
            if rate > 0:
                rates[afflic] = rate

        debuff_rates = {}
        for buff in self.all_buffs:
            if buff.get() and (buff.bufftype == 'debuff' or buff.name == 'simulated_def') and buff.val < 0:
                dkey = f'debuff_{buff.mod_type}'
                try:
                    debuff_rates[dkey] *= (1 - buff.chance)
                except:
                    debuff_rates[dkey] = 1 - buff.chance
                try:
                    debuff_rates['debuff'] *= (1 - buff.chance)
                except:
                    debuff_rates['debuff'] = 1 - buff.chance
        for dkey in debuff_rates.keys():
            debuff_rates[dkey] = 1 - debuff_rates[dkey]
        rates.update(debuff_rates)

        if self.conf['classbane']:
            enemy_class = self.conf['classbane']
            if self.condition(f'vs {enemy_class} enemy'):
                rates[enemy_class] = 1

        return rates if not as_list else list(rates.items())

    def killer_mod(self, name=None):
        total = self.mod('killer') - 1
        rate_list = self.build_rates()
        for mask in product(*[[0, 1]] * len(rate_list)):
            p = 1.0
            modifiers = defaultdict(lambda: set())
            for i, on in enumerate(mask):
                cond = rate_list[i]
                cond_name = cond[0]
                cond_p = cond[1]
                if on:
                    p *= cond_p
                    for order, mods in self.all_modifiers[f"{cond_name}_killer"].items():
                        for mod in mods:
                            modifiers[order].add(mod)
                else:
                    p *= 1 - cond_p
            total += p * reduce(operator.mul, [1 + sum([mod.get() for mod in order]) for order in modifiers.values()], 1.0)
        return total

    def def_mod(self):
        defa = min(1-self.mod('def', operator=operator.add), 0.5)
        defb = min(1-self.mod('defb', operator=operator.add), 0.3)
        return 1 - min(defa+defb, 0.5)

    def sp_mod(self, name):
        sp_mod = self.mod('sp', operator=operator.add)
        if name.startswith('fs'):
            sp_mod += self.mod('spf', operator=operator.add, initial=0)
        return sp_mod

    def sp_val(self, param):
        if isinstance(param, str):
            return self.sp_convert(
                self.sp_mod(param),
                self.conf[param].attr[0]['sp']
            )
        elif isinstance(param, int) and 0 < param:
            suffix = '' if self.current_x == 'default' else f'_{self.current_x}'
            return sum(
                self.sp_convert(
                    self.sp_mod('x'),
                    self.conf[f'x{x}{suffix}'].attr[0]['sp'])
                for x in range(1, param + 1)
            )

    def charged_in(self, param, sn):
        s = getattr(self, sn)
        return self.sp_val(param) + s.charged >= s.sp

    def have_buff(self, name):
        for b in self.all_buffs:
            if b.name.startswith(name) and b.get():
                return True
        return False

    def buffstack(self, name):
        return reduce(lambda s, b: s+int(b.get() and b.name == name), self.all_buffs, 0)

    @property
    def buffcount(self):
        buffcount = reduce(lambda s, b: s+int(b.get() and b.bufftype in ('self', 'team') and not b.hidden), self.all_buffs, 0)
        if self.conf['sim_buffbot.count'] is not None:
            buffcount += self.conf.sim_buffbot.count
        return buffcount

    def l_idle(self, e):
        """
        Listener that is called when there is nothing to do.
        """
        self.think_pin('idle')
        prev = self.action.getprev()
        if prev.name[0] == 's':
            self.think_pin(prev.name)
        if self.Skill._static.first_x_after_s:
            self.Skill._static.first_x_after_s = 0
            s_prev = self.Skill._static.s_prev
            self.think_pin('%s-x' % s_prev)
        return self.x()

    def getprev(self):
        prev = self.action.getprev()
        return prev.name, prev.index, prev.status

    def dragon(self, act_str=None):
        if act_str:
            return self.dragonform.act(act_str)
        return self.dragonform()

    def fs(self, n=None):
        fsn = 'fs' if n is None else f'fs{n}'
        if self.current_fs is not None:
            fsn += '_' + self.current_fs
        try:
            before = self.action.getdoing()
            if before.status == Action.STARTUP:
                before = self.action.getprev()
            if not self.a_fs_dict[fsn].enabled:
                return False
            return self.a_fs_dict[fsn](before.name)
        except KeyError:
            return False

    def x(self, x_min=1):
        prev = self.action.getprev()
        if self.deferred_x is not None:
            log('deferred_x', self.deferred_x)
            self.current_x = self.deferred_x
            self.deferred_x = None
        if isinstance(prev, X) and prev.group == self.current_x:
            if prev.index < self.conf[prev.group].x_max:
                x_next = self.a_x_dict[self.current_x][prev.index+1]
            else:
                x_next = self.a_x_dict[self.current_x][x_min]
            if x_next.enabled:
                return x_next()
            else:
                self.current_x = 'default'
        return self.a_x_dict[self.current_x][x_min]()

    def l_x(self, e):
        # FIXME: race condition?
        x_max = self.conf[self.current_x].x_max
        if e.index == x_max:
            log('x', e.name, 0, '-'*38 + f'c{x_max}')
        else:
            log('x', e.name, 0)
        self.hit_make(e, self.conf[e.name], cb_kind=f'x_{e.group}' if e.group != 'default' else 'x', pin='x')

    def dodge(self):
        return self.a_dodge()

    def l_dodge(self, e):
        log('dodge', '-')
        self.think_pin('dodge')

    def add_combo(self, name='#'):
        # real combo count
        delta = now()-self.last_c
        if delta <= self.ctime:
            self.hits += self.echo
        else:
            self.hits = self.echo
            log('combo', f'reset combo after {delta:.02}s')
        self.last_c = now()

    # def add_hits(self, hit):
    #     # potato combo count
    #     if hit is None:
    #         raise ValueError('none type hit')
    #     if hit < 0:
    #         self.hits = 0
    #         log('combo', 'reset combo')
    #     else:
    #         c_hits = self.hits
    #         for _ in range(hit):
    #             self.add_combo()
    #         return self.hits - c_hits
    #     return 0

    def load_aff_conf(self, key):
        confv = self.conf[key]
        if confv is None:
            return []
        if isinstance(confv, list):
            return confv
        if self.sim_afflict:
            aff = next(iter(self.sim_afflict))
            if confv[aff]:
                return confv[aff]
        return confv['base'] or []

    def config_coabs(self):
        if not self.conf['flask_env']:
            self.d_coabs()
            coab_list = self.load_aff_conf('coabs')
        else:
            coab_list = self.conf['coabs'] or []
        try:
            self_coab = list(self.slots.c.coabs.keys())[0]
        except:
            self_coab = self.__class__.__name__
        for name in coab_list:
            try:
                self.slots.c.coabs[name] = self.slots.c.valid_coabs[name]
            except KeyError:
                raise ValueError(f'No such coability: {name}')

    def rebind_function(self, owner, src, dst=None):
        dst = dst or src
        try:
            self.__setattr__(dst, getattr(owner, src).__get__(self, self.__class__))
        except AttributeError:
            pass

    @property
    def skills(self):
        return tuple(self.a_s_dict.values())

    def s(self, n):
        return self.a_s_dict[f's{n}']()

    @property
    def s1(self):
        return self.a_s_dict['s1']

    @property
    def s2(self):
        return self.a_s_dict['s2']

    @property
    def s3(self):
        return self.a_s_dict['s3']

    @property
    def s4(self):
        return self.a_s_dict['s4']

    def config_skills(self):
        self.current_s = {'s1': 'default', 's2': 'default', 's3': 'default', 's4': 'default'}
        self.Skill._static.current_s = self.current_s
        self.conf.s1.owner = None
        self.conf.s3.owner = None

        if not self.conf['flask_env']:
            self.d_skillshare()
            self.skillshare_list = self.load_aff_conf('share')
        else:
            self.skillshare_list = self.conf['share'] or []
        preruns = {}
        try:
            self.skillshare_list.remove(self.__class__.__name__)
        except ValueError:
            pass
        self.skillshare_list = list(OrderedDict.fromkeys(self.skillshare_list))
        if len(self.skillshare_list) > 2:
            self.skillshare_list = self.skillshare_list[:2]
        if len(self.skillshare_list) < 2:
            self.skillshare_list.insert(0, 'Weapon')

        from conf import load_adv_json, skillshare
        from core.simulate import load_adv_module
        self_data = skillshare.get(self.__class__.__name__, {})
        share_limit = self_data.get('limit', 10)
        sp_modifier = self_data.get('mod_sp', 1)
        self.skill_share_att = self_data.get('mod_att', 0.7)
        share_costs = 0

        for idx, owner in enumerate(self.skillshare_list):
            dst_key = f's{idx+3}'
            # if owner == 'Weapon' and (self.slots.w.noele or self.slots.c.ele in self.slots.w.ele):
            if owner == 'Weapon':
                s3 = self.slots.w.s3
                if s3:
                    self.conf.update(s3)
                    self.conf.s3.owner = None
            else:
                # I am going to spaget hell for this
                sdata = skillshare[owner]
                try:
                    share_costs += sdata['cost']
                except KeyError:
                    # not allowed to share skill
                    continue
                if share_limit < share_costs:
                    raise ValueError(f'Skill share exceed cost {(*self.skillshare_list, share_costs)}.')
                src_key = f's{sdata["s"]}'
                shared_sp = self.sp_convert(sdata['sp'], sp_modifier)
                try:
                    owner_conf = Conf(load_adv_json(owner))
                    for src_sn, src_snconf in owner_conf.find(f'^{src_key}(_[A-Za-z0-9]+)?$'):
                        dst_sn = src_sn.replace(src_key, dst_key)
                        self.conf[dst_sn] = src_snconf
                        self.conf[dst_sn].owner = owner
                        self.conf[dst_sn].sp = shared_sp
                    owner_module = load_adv_module(owner)
                    preruns[dst_key] = owner_module.prerun_skillshare
                    for sfn in ('before', 'proc'):
                        self.rebind_function(owner_module, f'{src_key}_{sfn}', f'{dst_key}_{sfn}')
                except:
                    pass
                # self.conf[dst_key].sp = shared_sp

        for sn, snconf in self.conf.find(r'^s\d(_[A-Za-z0-9]+)?$'):
            s = S(sn, snconf)
            if s.group != 'default' and self.conf[s.base]:
                snconf.update(self.conf[s.base], rebase=True)
            self.conf[s.base].p_max = 0
            if s.group.startswith('phase'):
                s.group = int(s.group[5:])
                try:
                    self.conf[s.base].p_max = max(self.conf[s.base].p_max, s.group)
                except ValueError:
                    self.conf[s.base].p_max = s.group
                self.current_s[s.base] = 0
                s.group -= 1
                s.act_event.group = s.group
            self.a_s_dict[s.base].add_action(s.group, s)
            self.damage_sources_check(sn, snconf)

        return preruns

    def run(self):
        global loglevel
        if not loglevel:
            loglevel = 0

        self.ctx.on()
        self.doconfig()
        logreset()

        self.l_idle = Listener('idle', self.l_idle)
        self.l_x = Listener('x', self.l_x)
        self.l_dodge = Listener('dodge', self.l_dodge)
        self.l_fs = Listener('fs', self.l_fs)
        self.l_s = Listener('s', self.l_s)
        # self.l_x           = Listener(['x','x1','x2','x3','x4','x5'],self.l_x)
        # self.l_fs          = Listener(['fs','x1fs','x2fs','x3fs','x4fs','x5fs'],self.l_fs)
        # self.l_s           = Listener(['s','s1','s2','s3'],self.l_s)
        self.l_silence_end = Listener('silence_end', self.l_silence_end)
        self.l_dmg_make = Listener('dmg_make', self.l_dmg_make)
        self.l_true_dmg = Listener('true_dmg', self.l_true_dmg)
        self.l_dmg_formula = Listener('dmg_formula', self.l_dmg_formula)
        self.l_set_hp = Listener('set_hp', self.l_set_hp)

        self.ctx.on()

        self.config_slots()

        preruns_ss = self.config_skills()

        # if self.conf.c.a:
        #     self.slots.c.a = list(self.conf.c.a)

        self.config_coabs()

        self.base_att = 0

        self.sim_buffbot()

        self.slots.oninit(self)
        self.base_att = int(self.slots.att)
        self.base_hp = int(self.slots.hp)

        self.hp = self.condition.prev_hp
        if 'hp' in self.conf:
            self.set_hp(self.conf['hp'])            

        for dst_key, prerun in preruns_ss.items():
            prerun(self, dst_key)
        self.prerun()

        if 'dragonbattle' in self.conf and self.conf['dragonbattle']:
            self._acl = self._acl_dragonbattle
            self.dragonform.set_dragonbattle(self.duration)
        elif 'acl' not in self.conf_init:
            if self._acl_default is None:
                self._acl_default = core.acl.build_acl(self.conf.acl)
            self._acl = self._acl_default
        else:
            self._acl = core.acl.build_acl(self.conf.acl)
        self._acl.reset(self)

        self.displayed_att = int(self.base_att * self.mod('att'))

        # from pprint import pprint
        # pprint(self.conf)

        Event('idle')()
        end, reason = Timeline.run(self.duration)
        self.base_buff.count_team_buff()
        log('sim', 'end', reason)

        self.post_run(end)

        # for aff, up in self.afflics.get_uptimes().items():
        #     if up > 0.10:
        #         if len(self.comment) > 0:
        #             self.comment += '; '
        #         self.comment += '{:.0%} {} uptime'.format(up, aff)

        # if g_logs.team_doublebuffs > 0:
        #     if len(self.comment) > 0:
        #         self.comment += '; '
        #     self.comment += f'{d/g_logs.team_doublebuffs:.2f}s team doublebuff interval'

        self.logs = copy.deepcopy(g_logs)

        return end

    def post_run(self, end):
        pass

    def debug(self):
        pass

    def _cb_think(self, t):
        if loglevel >= 2:
            log('think', '/'.join(map(str,(t.pin, t.dname, t.dstat, t.didx, t.dhit))))
        return self._acl(t)

    def _cb_think_fsf(self, t):
        if loglevel >= 2:
            log('think', '/'.join(map(str,(t.pin, t.dname, t.dstat, t.didx, t.dhit))))
        result = self._acl(t)
        if not result and self.current_x == 'default' and t.dstat >= 0 and t.pin[0] == 'x' and t.didx == 5 and t.dhit == 0:
            return self.fsf()
        return result

    def think_pin(self, pin):
        # pin as in "signal", says what kind of event happened

        if pin in self.conf.latency:
            latency = self.conf.latency[pin]
        else:
            latency = self.conf.latency.default

        doing = self.action.getdoing()

        t = Timer(self.cb_think)
        t.pin = pin
        t.dname = doing.name
        t.dstat = doing.status
        t.didx = doing.index
        t.dhit = int(doing.has_delayed)
        t.on(latency)

    def l_silence_end(self, e):
        doing = self.action.getdoing()
        sname = self.Skill._static.s_prev
        if doing.name[0] == 'x':
            self.Skill._static.first_x_after_s = 1
        else:
            self.think_pin(sname + '-x')  # best choice
        self.think_pin(sname)
        # if doing.name[0] == 's':
        #   no_deed_to_do_anythin

    # DL uses C floats and round SP up, which leads to precision issues
    @staticmethod
    def sp_convert(haste, sp):
        sp_hasted = c_float(c_float(haste).value * sp).value
        sp_int = int(sp_hasted)
        return sp_int if sp_int == sp_hasted else sp_int + 1

    def get_targets(self, target):
        # FIXME - make a shared sp skill class
        if target is None:
            return self.skills
        if isinstance(target, str):
            try:
                return [self.a_s_dict[target]]
            except KeyError:
                return None
        if isinstance(target, list):
            targets = []
            for t in target:
                try:
                    targets.append(self.a_s_dict[t])
                except KeyError:
                    continue
            return targets
        return None

    def charge_p(self, name, percent, target=None, no_autocharge=False):
        percent = percent / 100 if percent > 1 else percent
        targets = self.get_targets(target)
        if not targets:
            return
        for s in targets:
            if no_autocharge and hasattr(s, 'autocharge_timer'):
                continue
            s.charge(self.sp_convert(percent, s.sp))
        if isinstance(target, list):
            t_str = ','.join(target)
        else:
            t_str = target
        log('sp', name if not target else f'{name}->{t_str}', f'{percent*100:.0f}%', ', '.join([f'{s.charged}/{s.sp}' for s in self.skills]))

        if percent == 1:
            self.think_pin('prep')

    def charge(self, name, sp, target=None):
        # sp should be integer
        sp = self.sp_convert(self.sp_mod(name), sp)
        targets = self.get_targets(target)
        if not targets:
            return
        for s in targets:
            s.charge(sp)
        if isinstance(target, list):
            t_str = ','.join(target)
        else:
            t_str = target
        log('sp', name if not target else f'{name}_{t_str}', sp, ', '.join([f'{s.charged}/{s.sp}' for s in self.skills]))

        self.think_pin('sp')

    def l_dmg_formula(self, e):
        name = e.dname
        dmg_coef = e.dmg_coef
        if hasattr(e, 'dtype'):
            name = e.dtype
        if 'modifiers' in e.__dict__:
            if e.modifiers != None and e.modifiers != 0:
                self.all_modifiers = e.modifiers
        e.dmg = self.dmg_formula(name, dmg_coef)
        self.all_modifiers = self.modifier._static.all_modifiers
        e.ret = e.dmg
        return

    def dmg_formula(self, name, dmg_coef):
        dmg_mod = self.dmg_mod(name)
        att = 1.0 * self.att_mod(name) * self.base_att
        armor = 10 * self.def_mod()
        ele = (self.mod(self.slots.c.ele) + 0.5) * (self.mod(f'{self.slots.c.ele}_resist'))
        return 5.0 / 3 * dmg_coef * dmg_mod * att / armor * ele  # true formula

    def l_true_dmg(self, e):
        log('dmg', e.dname, e.count, e.comment)

    def l_dmg_make(self, e):
        try:
            return self.dmg_make(e.dname, e.dmg_coef, e.dtype)
        except AttributeError:
            return self.dmg_make(e.dname, e.dmg_coef)

    def l_attenuation(self, t):
        self.add_combo(name=t.dname)
        return self.dmg_make(t.dname, t.dmg_coef, t.dtype, attenuation=t.attenuation, depth=t.depth)

    def dmg_make(self, name, coef, dtype=None, fixed=False, attenuation=None, depth=0):
        if coef <= 0.01:
            return 0
        if dtype == None:
            dtype = name
        count = self.dmg_formula(dtype, coef) if not fixed else coef
        log('dmg', name, count)
        self.dmg_proc(name, count)
        if self.echo > 1:
            echo_count = self.dmg_formula_echo(coef)
            self.dmg_proc(name, echo_count)
            log('dmg', 'echo', echo_count, f'from {name}')
            count += echo_count
        if attenuation is not None:
            rate, pierce = attenuation
            if pierce != 0:
                coef *= rate
                depth += 1
                if depth == 1:
                    name = f'{name}_extra{depth}'
                else:
                    name = '_'.join(name.split('_')[:-1]) + f'_extra{depth}'
                t = Timer(self.l_attenuation)
                t.dname = name
                t.dmg_coef = coef
                t.dtype = dtype
                t.attenuation = (rate, pierce-1)
                t.depth = depth
                t.on(self.conf.attenuation.delay)
        return count

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None):
        g_logs.log_hitattr(name, attr)
        hitmods = self.actmods(name)
        if 'dmg' in attr:
            if 'killer' in attr:
                hitmods.append(KillerModifier(name, 'hit', *attr['killer']))
            if 'crisis' in attr:
                hitmods.append(CrisisModifier(name, attr['crisis'], self.hp))
            if 'bufc' in attr:
                hitmods.append(Modifier(f'{name}_bufc', 'att', 'bufc', attr['bufc']*self.buffcount))
            if 'fade' in attr:
                attenuation = (attr['fade'], self.conf.attenuation.hits)
            else:
                attenuation = None
            for m in hitmods:
                m.on()
            if 'extra' in attr:
                for _ in range(min(attr['extra'], self.buffcount)):
                    self.add_combo(name)
                    self.dmg_make(name, attr['dmg'], attenuation=attenuation)
            else:
                self.add_combo(name)
                self.dmg_make(name, attr['dmg'], attenuation=attenuation)

        if onhit:
            onhit(name, base, group, aseq)

        if 'sp' in attr:
            if isinstance(attr['sp'], int):
                if name.startswith('dx'):
                    self.dragonform.ds_charge(attr['sp'])
                else:
                    value = attr['sp']
                    self.charge(base, value)
            else:
                value = attr['sp'][0]
                mode = None if len(attr['sp']) == 1 else attr['sp'][1]
                target = None if len(attr['sp']) == 2 else attr['sp'][2]
                if target == 'sn':
                    target = base
                charge_f = self.charge
                if mode == '%':
                    charge_f = self.charge_p
                charge_f(base, value, target=target)

        if 'dp' in attr:
            self.dragonform.charge_gauge(attr['dp'])

        if 'utp' in attr:
            self.dragonform.charge_gauge(attr['utp'], utp=True)

        if 'hp' in attr:
            try:
                self.add_hp(float(attr['hp']))
            except TypeError:
                value = attr['hp'][0]
                mode = None if len(attr['hp']) == 1 else attr['hp'][1]
                if mode == '=':
                    self.set_hp(value)
                elif mode == '>':
                    if self.hp > value:
                        self.set_hp(value)
                elif mode == '%':
                    self.set_hp(self.hp*value)

        if 'afflic' in attr:
            aff_type, aff_args = attr['afflic'][0], attr['afflic'][1:]
            getattr(self.afflics, aff_type).on(name, *aff_args)

        if 'bleed' in attr:
            rate, mod = attr['bleed']
            if self.conf.mbleed or (rate < 100 and base[0] == 's' and self.a_s_dict[base].owner is not None):
                from module.bleed import mBleed
                bleed = mBleed(name, mod)
                if self.bleed is None:
                    self.bleed = bleed
                    self.bleed.reset()
                self.bleed = mBleed(name, mod, chance=rate/100, debufftime=self.mod('debuff', operator=operator.add))
                self.bleed.on()
            else:
                from module.bleed import Bleed
                bleed = Bleed(name, mod)
                if self.bleed is None:
                    self.bleed = bleed
                    self.bleed.reset()
                if rate == 100 or rate > random.uniform(0, 100):
                    self.bleed = Bleed(name, mod, debufftime=self.mod('debuff', operator=operator.add))
                    self.bleed.on()


        if 'buff' in attr:
            self.hitattr_buff_outer(name, base, group, aseq, attr)

        for m in hitmods:
            m.off()

    def hitattr_buff_outer(self, name, base, group, aseq, attr):
            bctrl = None
            blist = attr['buff']
            try:
                if blist[-1][0] == '-':
                    bctrl = blist[-1]
                    blist = blist[:-1]
            except TypeError:
                pass
            if bctrl:
                if bctrl == '-off':
                    try:
                        self.buff.off(*blist)
                    except:
                        pass
                    return
                if bctrl == '-refresh':
                    try:
                        return self.buff.on(base, group, aseq)
                    except KeyError:
                        pass
                if bctrl == '-replace':
                    self.buff.off_all(base, aseq)
                    try:
                        return self.buff.on(base, group, aseq)
                    except KeyError:
                        pass
                if bctrl.startswith('-overwrite'):
                    # does not support multi buffs
                    try:
                        ow_buff = self.buff.get_overwrite(bctrl)
                        v_current = abs(ow_buff.value())
                        v_new = abs(blist[1])
                        if v_current == v_new or (v_current > v_new and not ow_buff.get()):
                            ow_buff.on()
                            return
                    except:
                        pass
                    buff = self.hitattr_buff(name, base, group, aseq, 0, blist)
                    if buff:
                        self.buff.add_overwrite(base, group, aseq, buff.on(), bctrl)
                    return
            if isinstance(blist[0], list):
                buff_objs = []
                for bseq, attrbuff in enumerate(blist):
                    obj = self.hitattr_buff(name, base, group, aseq, bseq, attrbuff)
                    if obj:
                        buff_objs.append(obj)
                if buff_objs:
                    self.buff.add(base, group, aseq, MultiBuffManager(name, buff_objs).on())
            else:
                buff = self.hitattr_buff(name, base, group, aseq, 0, blist)
                if buff:
                    self.buff.add(base, group, aseq, buff.on())

    def hitattr_buff(self, name, base, group, aseq, bseq, attrbuff):
        btype = attrbuff[0]
        if btype in ('energy', 'inspiration'):
            getattr(self, btype).add(attrbuff[1], team=len(attrbuff) > 2 and bool(attrbuff[2]))
        else:
            bargs = attrbuff[1:]
            try:
                return bufftype_dict[btype](f'{name}_{aseq}{bseq}', *bargs)
            except ValueError:
                return None

    def l_hitattr_make(self, t):
        self.hitattr_make(t.name, t.base, t.group, t.aseq, t.attr, t.onhit)
        if t.pin is not None:
            self.think_pin(f'{t.pin}-h')
            p = Event(f'{t.pin}-h')
            p.is_hit = t.name in self.damage_sources
            p()
        if t.proc is not None:
            t.proc(t)
        if t.actmod:
            self.actmod_off(t)

    ATTR_COND = {
        'hp>': lambda s, v: s.hp > v,
        'hp>=': lambda s, v: s.hp >= v,
        'hp<': lambda s, v: s.hp < v,
        'hp<=': lambda s, v: s.hp <= v,
        'rng': lambda s, v: random.random() <= v,
        'hits': lambda s, v: s.hits >= v
    }
    def do_hitattr_make(self, e, aseq, attr, pin=None):
        if 'cond' in attr:
            condtype, condval = attr['cond']
            if not Adv.ATTR_COND[condtype](self, condval):
                return
        iv = attr.get('iv', 0)
        if not attr.get('nospd'):
            iv /= self.speed()
        try:
            onhit = getattr(self, f'{e.name}_hit{aseq+1}')
        except AttributeError:
            onhit = None
        if iv is not None and iv > 0:
            mt = Timer(self.l_hitattr_make)
            mt.pin = pin
            mt.name = e.name
            mt.base = e.base
            mt.group = e.group
            try:
                mt.index = e.index
            except AttributeError:
                pass
            try:
                mt.level = e.level
            except AttributeError:
                pass
            mt.aseq = aseq
            mt.attr = attr
            mt.onhit = onhit
            mt.proc = None
            mt.actmod = False
            mt.on(iv)
            if not attr.get('msl'):
                self.action.getdoing().add_delayed(mt)
            return mt
        else:
            e.pin = pin
            e.aseq = aseq
            e.attr = attr
            self.hitattr_make(e.name, e.base, e.group, aseq, attr, onhit)
            if pin is not None:
                p = Event(f'{pin}-h')
                p.is_hit = e.name in self.damage_sources
                p()
        return None

    def schedule_hits(self, e, conf, pin=None):
        final_mt = None
        if conf['attr']:
            prev_attr = None
            for aseq, attr in enumerate(conf['attr']):
                if isinstance(attr, str):
                    attr = getattr(self, attr, 0)
                if prev_attr is not None and isinstance(attr, int):
                    for repeat in range(1, attr):
                        res_mt = self.do_hitattr_make(e, aseq+repeat, prev_attr, pin=pin)
                else:
                    res_mt = self.do_hitattr_make(e, aseq, attr, pin=pin)
                    prev_attr = attr
                if res_mt is not None and (final_mt is None or res_mt.timing >= final_mt.timing):
                    final_mt = res_mt
        return final_mt

    def hit_make(self, e, conf, cb_kind=None, pin=None):
        cb_kind = cb_kind or e.name
        try:
            getattr(self, f'{cb_kind}_before')(e)
        except AttributeError:
            pass
        final_mt = self.schedule_hits(e, conf, pin=pin)
        proc = getattr(self, f'{cb_kind}_proc', None)
        if final_mt is not None:
            final_mt.actmod = True
            final_mt.proc = proc
        else:
            if proc:
                proc(e)
            self.actmod_off(e)
        self.think_pin(pin or e.name)

    def l_fs(self, e):
        log('cast', e.name)
        self.actmod_on(e)
        self.hit_make(e, self.conf[e.name], pin=e.name.split('_')[0])

    def l_s(self, e):
        if e.name == 'ds':
            return
        self.actmod_on(e)
        prev = self.action.getprev().name
        log('cast', e.name, f'after {prev}', ', '.join([f'{s.charged}/{s.sp}' for s in self.skills]))
        self.hit_make(e, self.conf[e.name], cb_kind=e.base)

    def c_fs(self, group):
        if self.current_fs == group and self.alt_fs_buff is not None:
            return self.alt_fs_buff.uses
        return 0

    def c_x(self, group):
        return self.current_x == group

    def c_s(self, seq, group):
        return self.current_s[f's{seq}'] == group

    @property
    def dgauge(self):
        return self.dragonform.dragon_gauge

    @property
    def bleed_stack(self):
        try:
            return self.bleed._static['stacks']
        except AttributeError:
            return 0

    def stop(self):
        doing = self.action.getdoing()
        if doing.status == Action.RECOVERY or doing.status == Action.OFF:
            Timeline.stop()
            return True
        return False
