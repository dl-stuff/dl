import heapq as hq
import itertools
from core.ctx import *


def now():
    return _g_now


def set_time(time):
    global _g_now
    _g_now = time


utp = 0
NOW = 1
AFTER = 2


def add_event_listener(eventname, listener, order=1):  # listener should be a function
    global _g_event_listeners

    if not eventname in _g_event_listeners:
        _g_event_listeners[eventname] = [[], [], []]
    _g_event_listeners[eventname][order].append(listener)


def remove_event_listener(eventname, listener):
    if not eventname in _g_event_listeners:
        return
    for orders in _g_event_listeners[eventname]:
        try:
            orders.remove(listener)
        except ValueError:
            continue


def get_event_trigger(eventname, trigger=[]):
    global _g_event_listeners
    if eventname not in _g_event_listeners:
        _g_event_listeners[eventname] = [[], [], []]
    return _g_event_listeners[eventname]


class Event(object):
    def __init__(self, name=None):
        if name:
            self.name = name
            self.__name = name
            self._trigger = get_event_trigger(name)
        else:
            self._trigger = []

    def listener(self, cb, eventname=None, order=1):
        if eventname:
            if type(eventname) == list or type(eventname) == tuple:
                for i in eventname:
                    add_event_listener(i, cb, order)
            else:
                add_event_listener(eventname, cb, order)
        else:
            add_event_listener(self.__name, cb, order)

    def on(self, e=None):
        for orders in self._trigger:
            for cb in orders:
                cb(self)

    def __call__(self, expand=None):
        self.on(self)

    # def __str__(self):
    #     return self.__name

    # __call__ = on


# } class Event


class Listener(object):
    def __init__(self, eventname, cb, order=1):
        self.__cb = cb
        self.__eventname = eventname
        self.__online = 0
        self.__order = order
        self.on()

    def __call__(self, e):
        self.__cb(e)

    def get(self):
        return bool(self.__online)

    def on(self, cb=None):
        if self.__online:
            return
        if cb:
            self.__cb = cb
        if type(self.__eventname) == list or type(self.__eventname) == tuple:
            for i in self.__eventname:
                add_event_listener(i, self.__cb, self.__order)
        else:
            add_event_listener(self.__eventname, self.__cb, self.__order)
        self.__online = 1
        return self

    def pop(self):
        self.off()
        return self.__cb

    def set_cb(self, cb):
        self.__cb = cb

    def off(self):
        if not self.__online:
            return
        if type(self.__eventname) == list or type(self.__eventname) == tuple:
            for i in self.__eventname:
                remove_event_listener(i, self.__cb)
        else:
            remove_event_listener(self.__eventname, self.__cb)
        self.__online = 0
        return self


# } class Listener


class Timer(object):
    def __init__(self, proc=None, timeout=None, repeat=0, timeline=None):
        self.process = proc or self._process
        self.timeout = timeout or 0
        self.callback = self.callback_repeat if repeat else self.callback_once
        self.timeline = timeline or _g_timeline

        self.began = None
        self._elapsed = None
        self.timing = 0
        self.online = 0
        self.canceled = False

        self.pause_time = -1
        # self.on()

    def elapsed(self):
        if self.began is None:
            return self._elapsed or 0
        else:
            self._elapsed = _g_now - self.began
            return _g_now - self.began

    def timeleft(self):
        if self.pause_time > 0:
            return self.pause_time
        return self.timing - _g_now

    def on(self, timeout=None):
        if timeout:
            self.timeout = timeout
            self.timing = _g_now + timeout
        else:
            self.timing = _g_now + self.timeout
        self.canceled = False
        if self.online == 0:
            self.online = 1
        self.pause_time = -1
        self.timeline.add(self)
        self.began = _g_now
        return self

    def off(self):
        if self.online:
            self.online = 0
            self.canceled = True
            try:
                self.timeline.rm(self)
            except:
                pass
            self._elapsed = _g_now - self.began
            self.began = None
        return self

    def add(self, time=0):
        # core.log.log('timeline', self.timing, self.timing+time, time, self.timing+time-now())
        if self.pause_time > 0:
            self.pause_time += time
        else:
            self.timeout += time
            self.timing += time
            if self.timing < now():
                self.off()
            elif self.online:
                self.timeline.add(self)
            return self.timing - now()

    # alias
    disable = off
    enable = on
    __call__ = on

    def status(self):
        return self.online

    def callback_repeat(self):
        self.process(self)
        if self.timing == _g_now and self.online:
            self.timing += self.timeout
            self.timeline.add(self)

    def callback_once(self):
        self.process(self)
        if self.timing <= _g_now and self.online:
            self.online = 0
            self._elapsed = _g_now - self.began
            self.began = None
            # self.timeline.rm(self)

    def callback(self):
        pass

    def pause(self):
        if self.online:
            self.pause_time = self.timing - _g_now
            if self.pause_time > 0:
                self.off()
            return self

    def resume(self):
        if self.pause_time > 0:
            self.on(self.pause_time)
            self.pause_time = -1
            return self

    def __repr__(self):
        # return '%f: Timer:%s'%(self.timing,self.process)
        # return f'{self.timing}: {self.process}'
        return f"{hex(id(self))}: {self.process}"

    def _process(self, _):
        # sample plain _process
        # print("-- plain timer ", "@", t.timing)
        return 1


class Timeline(object):
    REMOVED = "<REMOVED>"

    def __init__(self):
        self._tlist = []
        self._tmap = {}
        self._tseq = itertools.count()

    def add(self, t):
        # self._tlist.append(t)
        if t in self._tmap:
            self.rm(t)
        count = next(self._tseq)
        entry = [t.timing, count, t]
        self._tmap[t] = entry
        hq.heappush(self._tlist, entry)

    def rm(self, t):
        # i = self._tlist.index(t)
        # return self._tlist.pop(i)
        entry = self._tmap.pop(t)
        entry[-1] = Timeline.REMOVED

    def pop(self):
        from pprint import pprint

        while self._tlist:
            timing, _, t = hq.heappop(self._tlist)
            if t is not Timeline.REMOVED:
                del self._tmap[t]
                return t
        # raise RuntimeError('Timeline error', self._tlist)

    def process_head(self):
        global _g_now
        tnext = self.pop()
        if not tnext:
            return -1
        if tnext.timing >= _g_now:
            _g_now = tnext.timing
            tnext.callback()
        else:
            raise RuntimeError(f"Timeline error {tnext.timing:.03f} < {_g_now:.03f} - {tnext}")
        return 0
        # tcount = len(self._tlist)
        # if tcount == 0:
        #     return -1

        # if tcount == 1:
        #     headtiming = self._tlist[0].timing
        #     headindex = 0
        # else: #if tcount >= 2:
        #     headtiming = self._tlist[0].timing
        #     headindex = 0
        #     for i in range(1,tcount):
        #         timing = self._tlist[i].timing
        #         if timing < headtiming:
        #             headtiming = timing
        #             headindex = i

        # if headtiming >= _g_now:
        #     _g_now = headtiming
        #     headt = self._tlist[headindex]
        #     headt.callback()
        # else:
        #     raise RuntimeError('Timeline error', headtiming, _g_now)
        # return 0

    @classmethod
    def run(cls, last=100):
        global _g_timeline
        return _g_timeline._run(last)

    @classmethod
    def stop(cls, last=100):
        global _g_timeline
        return _g_timeline._stop()

    def _stop(self):
        global _g_stop
        _g_stop = 1

    def _run(self, last=100):
        last += _g_now
        while 1:
            if _g_now > last:
                return _g_now, "timeout"

            r = self.process_head()
            if r == -1:
                return _g_now, "empty"

            if _g_stop:
                return _g_now, "forced"

    def __str__(self):
        return "Timeline tlist: %s" % (str(self._tlist))


# } class Timeline


Ctx().on()
Ctx.register(
    globals(),
    {
        "_g_now": 0,
        "_g_stop": 0,
        "_g_timeline": Timeline(),
        "_g_event_listeners": {},
    },
)


def main():
    class A:
        name = "b"

        def a3(self):
            print("-3", self.name)

    a = A()

    def a1():
        print("-1", now())

    def a2():
        e = Event("e3")
        e.test = 1
        e()
        print("-2", now())

    def lis(e):
        print("listener1")

    def lis2(e):
        print("listener2")

    def lis3(e):
        print("listener3")

    e1 = Timer(a1, 1).on()

    Event("e3").listener(lis3)
    Event("e2").listener(lis)
    Event("e2").listener(lis2)

    e2 = Timer(a2, 2).on()
    e3 = Timer(a.a3, 3).on()

    _g_timeline.run()


if __name__ == "__main__":
    main()
