from conf import load_all_equip_json

OUTPUT_DIR = 'www/dl-sim/page'

def validate(entry):
    if entry['dps'] == 0:
        return False
    if entry['team'] == 0:
        return False
    if len(entry['slots.a']) != 5:
        return False
    if len(entry['coabs']) != 3:
        return False
    if len(entry['share']) != 2:
        return False

def combine_equip():
    advequip = load_all_equip_json()
    sorted_outputs = {
        '60': [],
        '120': [],
        '180': []
    }

    for adv, equip in advequip.items():
        for duration, equip_d in equip.items():
            pref = equip_d.get('pref', 'base')
            for kind, entry in equip_d.items():
                if kind == 'pref':
                    continue
                if not validate(entry):
                    print('Skipping', adv, kind)
                    continue
                output = entry['output']
                if kind != pref and entry.get('tdps'):
                    tdps = entry.get('tdps')
                    output = output.replace(f'-,{duration},_', f'-,{duration},{tdps}')
                sorted_outputs[duration].append(output)

    for duration, outputs in sorted_outputs.items():
        dst = os.path.join(OUTPUT_DIR, f'{duration}.csv')
        with open(dst, 'w') as f:
            for out in outputs:
                f.write(out)

