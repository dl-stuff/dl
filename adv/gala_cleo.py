from core.advbase import *

import random
random.seed()

def module():
    return Gala_Cleo


class Gala_Cleo(Adv):
    comment = '(the true cleo is here)'
    conf = {}
    conf['slots.a'] = ['Candy_Couriers', 'Primal_Crisis']  # wand c2*1.08 = 217
    conf['acl'] = """
        `dragon(c3-s-end), x=5 and self.trickery <= 1
        `s3, not buff(s3)
        `fs, s1.charged>=s1.sp and c_fs(gleozone) > 0
        if x=5 or x=4 or fsc or s
        `s4
        `s2
        end
        `s1, s or fsc

        # Buffbot Gleo
        # https://wildshinobu.pythonanywhere.com/ui/dl_simc.html?conf=eyJhZHYiOiJnYWxhX2NsZW8iLCJkcmEiOiJSYW1pZWwiLCJ3ZXAiOiJBZ2l0bzJfSml1X0NpIiwid3AxIjoiQ2FuZHlfQ291cmllcnMiLCJ3cDIiOiJNZW1vcnlfb2ZfYV9GcmllbmQiLCJzaGFyZSI6WyJTdW1tZXJfQ2xlbyJdLCJjb2FiIjpbIklleWFzdSIsIkJvdyIsIkF1ZHJpYyJdLCJ0IjoiMTIwIiwidGVhbWRwcyI6IjMwMDAwIiwiYWNsIjoiYGRyYWdvbi5hY3QoJ3MgZW5kJyksIHM9MlxuYHMzLCBub3Qgc2VsZi5zM19idWZmXG5gZnMsIChzMS5jaGVjaygpIG9yIHMyLmNoZWNrKCkpIGFuZCBzZWxmLmZzX2FsdC51c2VzID4gMFxuYHMyLCBjYW5jZWxcbmBzMSwgY2FuY2VsXG5gczQsIHM9MSIsImNvbmRpdGlvbiI6eyJhMSBidWZmIGZvciAxMHMiOnRydWUsImJ1ZmYgYWxsIHRlYW0iOnRydWUsImhpdDE1Ijp0cnVlfX0=
        """
    conf['coabs'] = ['Blade','Bow','Dagger']
    conf['share'] = ['Curran']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
