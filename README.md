# dragalia lost sim and analysis

## Running
Python 3.7+

```
python adv/[someone].py [loglevel(-4,-3,-2,-1,0,1,2)] [teamdps] [mass]
```
or
```
./sim [someone] [loglevel(-4,-3,-2,-1,0,1,2)] [teamdps] [mass]
```
or
```
./sim.bat [someone] [loglevel(-4,-3,-2,-1,0,1,2)] [teamdps] [mass]
```

loglevel:
- 0: default report
- 1: detailed log
- 2: python code transpiled from ACL
- -2: CSV format
- -5: sim with 100% affliction

```python adv/mikoto.py``` show basic result of Mikoto's simulation

```python adv/maribelle.py 1``` show result and combo loop of Maribelle

```python adv/gala_sarisse.py -2 180 10000``` show result of Gala Sarisse for 180s with 10000 team dps

```python adv/valerio.py -2 60 10000 1000``` show mass sim averaged 1000 run result of Valerio for 60s with 10000 team dps

## Documentation
Please consult the [wiki](https://github.com/dl-stuff/dl/wiki)
