import sys
import os
from setuptools import setup
from Cython.Build import cythonize

def run():
    CORE = [
        'core/ability.py',
        'core/acl.py',
        'core/advbase.py',
        'core/afflic.py',
        'core/condition.py',
        'core/config.py',
        'core/ctx.py',
        'core/dragonform.py',
        'core/dummy.py',
        'core/log.py',
        'core/modifier.py',
        'core/simulate.py',
        'core/timeline.py',
        'module/template.py',
        'module/bleed.py',
        'module/tension.py'
    ]

    ADV = [
        'adv/gala_luca.py',
        'adv/incognito_nefaria.py',
        'adv/valerio.py'
    ]
    with open('chara_slow.txt', 'r') as f:
        for line in f:
            ADV.append(f'adv/{line.strip()}')

    setup(
        name='core',
        ext_modules=cythonize(
            CORE+ADV,
            compiler_directives={'language_level' : '3'},
        ),
        zip_safe=False,
    )


if __name__ == '__main__':
    run()