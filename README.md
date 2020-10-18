# dragalia lost sim and analysis

## Running

Requirements: Python 3.7+, [lark-parser](https://github.com/lark-parser/lark)

```
python adv/[someone].py [loglevel(-4,-3,-2,-1,0,1,2)] [mass]
```
or
```
./sim [someone] [loglevel(-4,-3,-2,-1,0,1,2)] [mass]
```
or
```
./sim.bat [someone] [loglevel(-4,-3,-2,-1,0,1,2)] [mass]
```

loglevel:
- 0: default report
- 1: detailed log
- 2: ACL parse tree
- -2: CSV format
- -5: sim with 100% affliction, show CSV
- -6: sim with 100% affliction, show default report

```python adv/mikoto.py``` show basic result of Mikoto's simulation

```python adv/maribelle.py 1``` show result and combo loop of Maribelle

```python adv/eugene.py -2 60 1000``` show mass sim averaged 1000 run result of Eugene for 60s

## Documentation
Please consult the [wiki](https://github.com/dl-stuff/dl/wiki)
