import sys
import json


INDENT = '    '

def recurse(data, k=None, depth=0, f=sys.stdout):
    if depth >= 2:
        if k == 'attr':
            r_str_lst = []
            end = len(data) - 1
            for idx, d in enumerate(data):
                if isinstance(d, int):
                    r_str_lst.append(' '+str(d))
                elif idx > 0:
                    r_str_lst.append('\n'+INDENT*(depth+1)+json.dumps(d))
                else:
                    r_str_lst.append(json.dumps(d))

            return '[\n' + INDENT*(depth+1) + (',').join(r_str_lst) + '\n' + INDENT*depth + ']' 
        return json.dumps(data)
    f.write('{\n')
    # f.write(INDENT*depth)
    end = len(data) - 1
    for idx, kv in enumerate(data.items()):
        k, v = kv
        f.write(INDENT*(depth+1))
        f.write('"')
        f.write(k)
        f.write('": ')
        res = recurse(v, k, depth+1, f)
        if res is not None:
            f.write(res)
        if idx < end:
            f.write(',\n')
        else:
            f.write('\n')
    f.write(INDENT*depth)
    f.write('}')


if __name__ == '__main__':
    with open('advconf.json', 'r') as f:
        gdata = json.load(f)
    # recurse(gdata)

    for adv, conf in gdata.items():
        conf['c']['name'] = adv
        conf['c']['spiral'] = conf['c']['lv2_autos']
        del conf['c']['lv2_autos']
        with open(f'adv/{adv}.json', 'w') as f:
            recurse(conf, f=f)
