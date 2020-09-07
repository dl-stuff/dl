import sys
import os
from setuptools import setup
from Cython.Build import cythonize

def run():
    CORE = [
        'core/acl.py',
        'core/advbase.py',
        'core/afflic.py',
        'core/condition.py',
        'core/config.py',
        'core/ctx.py',
        'core/dragonform.py',
        'core/dummy.py',
        'core/log.py',
        'core/simulate.py',
        'core/timeline.py',
        'module/bleed.py',
        'module/tension.py',
        'module/x_alt.py'
    ]

    setup(
        name='core',
        ext_modules=cythonize(
            CORE,
            compiler_directives={'language_level' : '3'},
        ),
        zip_safe=False,
    )


if __name__ == '__main__':
    run()