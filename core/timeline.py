import heapq
from core.ctx import *
import core.log


def now():
    return _g_now


def set_time(time):
    global _g_now
    _g_now = time


def add_event_listener(eventname, listener):  # listener should be a function
    global _g_event_listeners

    if eventname in _g_event_listeners:
        _g_event_listeners[eventname].append(listener)
    else:
        _g_event_listeners[eventname] = [listener]


def get_event_trigger(eventname, trigger=[]):
    global _g_event_listeners
    if eventname in _g_event_listeners:
        return _g_event_listeners[eventname]
    else:
        _g_event_listeners[eventname] = []
        return _g_event_listeners[eventname]


class Event(object):
    def __init__(self, name=None):
        if name:
            self.name = name
            self.__name = name
            self._trigger = get_event_trigger(name)
        else:
            self._trigger = []

    def listener(self, cb, eventname=None):
        if eventname:
            if type(eventname) == list or type(eventname) == tuple:
                for i in eventname:
                    add_event_listener(i, cb)
            else:
                add_event_listener(eventname, cb)
        else:
            add_event_listener(self.__name, cb)

    def on(self, e=None):
        for i in self._trigger:
            i(self)

    def __call__(self, expand=None):
        self.on(self)

    def __str__(self):
        return self.__name

    # __call__ = on


# } class Event

class Listener(object):
    def __init__(self, eventname, cb):
        self.__cb = cb
        self.__eventname = eventname
        self.__online = 0
        self.on()

    def __call__(self, e):
        self.__cb(e)

    def on(self, cb=None):
        if self.__online:
            return
        if cb:
            self.__cb = cb
        if type(self.__eventname) == list or type(self.__eventname) == tuple:
            for i in self.__eventname:
                add_event_listener(i, self.__cb)
        else:
            add_event_listener(self.__eventname, self.__cb)
        self.__online = 1
        return self

    def pop(self):
        self.off()
        return self.__cb

    def off(self):
        if not self.__online:
            return
        if type(self.__eventname) == list or type(self.__eventname) == tuple:
            for i in self.__eventname:
                els = get_event_trigger(i)
                idx = els.index(self.__cb)
                els.pop(idx)
        else:
            els = get_event_trigger(self.__eventname)
            idx = els.index(self.__cb)
            els.pop(idx)
        self.__online = 0
        return self


# } class Listener


class TimelineTrigger:
    def __init__(self, callback, timing):
        self.callback = callback
        self.timing = timing
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def process(self):
        if not self.cancelled:
            self.callback()

    def __lt__(self, other):
        return self.timing < other.timing


class Timer(object):
    def __init__(self, proc=None, timeout=None, repeat=0, timeline=None):
        if proc:
            self.process = proc
        else:
            self.process = self._process

        if timeout:
            self.timeout = timeout
        else:
            self.timeout = 0

        if repeat:
            self.callback = self.callback_repeat
        else:
            self.callback = self.callback_once

        if timeline:
            self.timeline = timeline
        else:
            self.timeline = _g_timeline

        self._timing = 0
        self.trigger = None

    @property
    def online(self):
        return self.trigger is not None

    @property
    def timing(self):
        return self._timing

    @timing.setter
    def timing(self, timing):
        if self.online:
            self.off()
            self._timing = timing
            self._trigger_on()
        else:
            self._timing = timing

    def on(self, timeout=None):
        if timeout:
            self.timeout = timeout
            self._timing = _g_now + timeout
        else:
            self._timing = _g_now + self.timeout

        self.off()
        self._trigger_on()
        return self

    def _trigger_on(self):
        self.trigger = TimelineTrigger(self.callback, self.timing)
        self.timeline.add(self.trigger)

    def off(self):
        if self.online:
            self.trigger.cancel()
            self.trigger = None
        return self

    def add(self, time=0):
        self.timeout += time
        self.timing += time

    # alias
    disable = off
    enable = on
    __call__ = on

    def status(self):
        return self.online

    def callback_repeat(self):
        self.callback_once()
        self.on()

    def callback_once(self):
        self.trigger = None
        self.process(self)

    def callback(self):
        pass

    def __str__(self):
        return '%f: Timer:%s' % (self.timing, self.process)

    def __repr__(self):
        return '%f: Timer:%s' % (self.timing, self.process)

    def _process(self):
        # sample plain _process
        print('-- plain timer ', '@', t.timing)
        return 1


def schedule(callback, timeout):
    global _g_timeline
    trigger = TimelineTrigger(callback, now() + timeout)
    _g_timeline.add(trigger)
    return trigger


class Timeline(object):
    def __init__(self):
        self._tlist = []

    def add(self, t):
        heapq.heappush(self._tlist, (t.timing, t))

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
        global _g_now
        last += _g_now
        while True:
            if _g_now > last or not self._tlist:
                return _g_now

            headt = heapq.heappop(self._tlist)[1]
            if headt.timing >= _g_now:
                _g_now = headt.timing
                headt.process()
            else:
                raise RuntimeError('Timing of next trigger is before current time')

            if _g_stop:
                return _g_now

    def __str__(self):
        return 'Timeline tlist: %s' % (str(self._tlist))


# } class Timeline


Ctx().on()
Ctx.register(globals(), {
    '_g_now': 0,
    '_g_stop': 0,
    '_g_timeline': Timeline(),
    '_g_event_listeners': {},
})


def main():
    class A():
        name = 'b'

        def a3(self):
            print('-3', self.name)

    a = A()

    def a1():
        print('-1', now())

    def a2():
        e = Event('e3')
        e.test = 1
        e()
        print('-2', now())

    def lis(e):
        print('listener1')

    def lis2(e):
        print('listener2')

    def lis3(e):
        print('listener3')

    e1 = Timer(a1, 1).on()

    Event('e3').listener(lis3)
    Event('e2').listener(lis)
    Event('e2').listener(lis2)

    e2 = Timer(a2, 2).on()
    e3 = Timer(a.a3, 3).on()

    _g_timeline.run()


if __name__ == '__main__':
    main()