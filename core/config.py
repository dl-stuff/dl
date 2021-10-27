import re


def _split(k):
    if k == ".":
        raise ValueError("Do not split .")
    return k.split(".", 1)


class Conf(dict):
    def __init__(self, conf=None, parent=None):
        self._parent = parent
        super().__init__()
        if isinstance(conf, dict):
            self.update(conf)

    def __getitem__(self, k):
        try:
            try:
                k0, kn = _split(k)
                return super().__getitem__(k0)[kn]
            except ValueError:
                return super().__getitem__(k)
        except KeyError:
            return None

    def __setitem__(self, k, v):
        try:
            k0, kn = _split(k)
            try:
                super().__getitem__(k0)[kn] = v
            except KeyError:
                super().__setitem__(k0, Conf(parent=self))
                super().__getitem__(k0)[kn] = v
        except ValueError:
            if isinstance(v, Conf):
                v._parent = self
                super().__setitem__(k, v)
            elif isinstance(v, dict):
                super().__setitem__(k, Conf(conf=v, parent=self))
            else:
                super().__setitem__(k, v)

    def __delitem__(self, k):
        try:
            k0, _ = _split(k)
            super().__delitem__(k0)
        except ValueError:
            super().__delitem__(k)

    def __getattr__(self, k):
        if k[0] == "_" or k in self.__dict__:
            return super().__getattribute__(k)
        try:
            return super().__getitem__(k)
        except KeyError:
            super().__setitem__(k, Conf(parent=self))
            return super().__getitem__(k)

    def __setattr__(self, k, v):
        if k[0] == "_" or k in self.__dict__:
            return super().__setattr__(k, v)
        if isinstance(v, Conf):
            super().__setitem__(k, v)
        elif isinstance(v, dict):
            super().__setitem__(k, Conf(conf=v, parent=self))
        else:
            super().__setitem__(k, v)

    def update(self, other, rebase=False):
        for k, v in other.items():
            if isinstance(v, dict):
                if k in ("interrupt", "cancel"):
                    if not rebase and not k in self:
                        self[k] = Conf(conf=v, parent=self)
                else:
                    try:
                        self[k].update(v, rebase=rebase)
                    except (AttributeError, KeyError):
                        self[k] = Conf(conf=v, parent=self)
                # except KeyError:
                #     self[k] = Conf(conf=v, parent=self)
            elif not (rebase and k in self):
                self[k] = v

    def __add__(self, other):
        res = Conf()
        res.update(self)
        res.update(other)
        return res

    @property
    def _value(self):
        try:
            return super().__getitem__(".")
        except KeyError:
            return None

    def find(self, pattern):
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        return filter(lambda c: pattern.match(c[0]), self.items())


if __name__ == "__main__":
    from pprint import pprint

    t1 = {
        "sp": 10725,
        "startup": 0.0,
        "recovery": 0.96667,
        "attr": [{"heal": 30, "iv": 0.16667}],
        "energizable": True,
        "cancel": {"any": 0.83333},
    }
    t2 = {
        "sp": 10725,
        "startup": 0.0,
        "recovery": 2.46667,
        "attr": [{"utp": -1500}, {"sp": [0.5, "%", "s2"]}, {"dmg": 32.5, "crisis": -0.9, "iv": 1.33333}],
    }

    t2c = Conf(t2)
    pprint(t2c)
    t1c = Conf(t1)
    t2c.update(t1c, rebase=True)
    pprint(t2c)
