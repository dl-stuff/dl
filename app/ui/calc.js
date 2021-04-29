const MODIFIERS = [
    ['att', 'passive', 0.2],
    ['att', 'buff'],
    ['att', 'ex', 0.1, 0, 0.1],
    ['skill', 'passive', 0.4],
    ['skill', 'buff'],
    ['skill', 'ex', 0.15, 0, 0.15],
    ['fs', 'passive', 0.55],
    ['fs', 'buff'],
    ['fs', 'ex', 0.2, 0, 0.2],
    ['x', 'ex', 0.2],
    ['crit', 'chance', 0.12, 0, 1],
    ['crit', 'damage', 0.7],
    ['punisher', 'passive', 0.5],
    ['punisher', 'broken'],
    ['ele', 'passive', 0.5],
    // ['enemy', 'defense_down'],
    // ['enemy', 'eleres_down'],
];
const EFFECTIVE_GROUPS = {
    'any': 'Any',
    'x': 'Auto',
    'skill': 'Skill',
    'fs': 'Force Strike',
}
const ACTION_SPECIFIC = ['skill', 'fs', 'x'];
const DRAGON_AURA = {
    'Reborn': [
        ['att', 'passive', 0.7],
        ['ele', 'passive', 0.3],
    ],
    'Sak-Siren-Vayu-Shinobi': [
        ['att', 'passive', 0.2],
        ['skill', 'passive', 0.9],
    ],
    'CatSith': [
        ['skill', 'buff', 1.8],
    ],
    'Arsene': [
        ['skill', 'passive', 1.8],
    ],
    'Mars': [
        ['att', 'passive', 0.9],
    ],
    'Fatalis-Garland': [
        ['att', 'passive', 0.8],
    ],
    'Mid0': [
        ['att', 'passive', 0.35],
        ['skill', 'passive', 0.7],
    ],
    'DKRathalos': [
        ['att', 'passive', 0.55],
        ['fs', 'passive', 0.6],
    ],
    'DJeanne-Giovanni': [
        ['crit', 'chance', 0.2],
        ['att', 'passive', 0.45],
    ],
    'Arctos-Nimis-Long2': [
        ['crit', 'damage', 0.55],
        ['att', 'passive', 0.45],
    ],
    'Apollo-Pazuzu-CPhoenix-Epi': [
        ['punisher', 'passive', 0.2],
        ['att', 'passive', 0.5],
    ]
}

function makeModifierItem(mtype, morder, init, min, max) {
    const holder = $('<div></div>').attr({ class: "col-sm-2" });
    const modId = `modifier-${mtype}-${morder}`;
    const label = $(`<label>${mtype}.${morder}</label>`).attr({ for: modId });
    const input = $('<input/>').attr({
        id: modId,
        class: "form-control",
        type: "number",
        min: (min) ? min : -1,
        max: (max) ? max : 100,
        step: 0.01,
        value: (init) ? init : 0,
    });
    input.data('mtype', mtype);
    input.data('morder', morder);
    input.change(calculateEffective);
    holder.append(label);
    holder.append(input);

    return holder;
}
function makeEffectiveOutputs(category, return_lst, no_label) {
    const effOut = [];
    for (const key of Object.keys(EFFECTIVE_GROUPS)) {
        const holder = $('<div></div>').attr({ class: "col-sm" });
        const effId = `${category}-${key}`;
        const input = $('<input/>').attr({
            id: effId,
            class: "form-control",
            type: "number",
            value: 1,
            readonly: true
        });
        if (!no_label) {
            const label = $(`<label>${EFFECTIVE_GROUPS[key]}</label>`).attr({ for: effId });
            holder.append(label);
        }
        holder.append(input);
        if (!return_lst) {
            $(`#${category}`).append(holder);
        } else {
            effOut.push(holder);
        }
    }
    return effOut;
}
function appendDragonAuraEntry(category, mods) {
    let modTxt = '';
    for (const mod of mods) {
        modTxt += ` ${mod[0]}.${mod[1]} ${mod[2]}`;
    }
    const title = $(`<div class="form-row"><legend class="col">${category}<span class="small">${modTxt}</span></legend></div>`);
    const output = $(`<div id="${category}" class="form-row"></div>`);
    for (const outHolder of makeEffectiveOutputs(category, true)) {
        output.append(outHolder);
    }
    const outputRelative = $(`<div id="${category}-relative" class="form-row"></div>`);
    for (const outHolder of makeEffectiveOutputs(`${category}-relative`, true, true)) {
        outputRelative.append(outHolder);
    }
    $('#modifier-form').append(title);
    $('#modifier-form').append(output)
    $('#modifier-form').append(outputRelative);
}
function sumInputBrackets() {
    const brackets = { 'crit': {} };
    $('#modifiers input').each((index, input) => {
        const mtype = $(input).data('mtype');
        const morder = $(input).data('morder');
        const value = parseFloat($(input).val());
        if (mtype == 'crit' || ACTION_SPECIFIC.includes(mtype)) {
            if (!brackets[mtype]) {
                brackets[mtype] = {}
            }
            if (mtype == 'crit' && morder == 'chance') {
                brackets[mtype][morder] = value;
            } else {
                brackets[mtype][morder] = (1 + value);
            }
        } else {
            brackets[`${mtype}-${morder}`] = (1 + value);
        }
    });
    return brackets;
}
function calculateEffectivePerCategory(category, inputBrackets, baseResults) {
    const brackets = JSON.parse(JSON.stringify(inputBrackets));
    if (DRAGON_AURA[category]) {
        for (const mod of DRAGON_AURA[category]) {
            const mtype = mod[0];
            const morder = mod[1];
            const value = mod[2];
            if (mtype == 'crit' || ACTION_SPECIFIC.includes(mtype)) {
                if (!brackets[mtype]) {
                    brackets[mtype] = {}
                }
                if (mtype == 'skill' && morder == 'buff') {
                    brackets[mtype][morder] = Math.min(3, brackets[mtype][morder] + value);
                } else {
                    brackets[mtype][morder] += value;
                }
            } else {
                brackets[`${mtype}-${morder}`] += value;
            }
        }
    }
    if (brackets['crit']) {
        brackets['critical'] = (brackets['crit']['chance'] * brackets['crit']['damage']) + (1 - brackets['crit']['chance']);
    }
    const results = {
        any: 1,
        x: 1,
        skill: 1,
        fs: 1
    }
    for (const key of Object.keys(brackets)) {
        if (ACTION_SPECIFIC.includes(key)) {
            for (const key2 of Object.keys(brackets[key])) {
                results[key] *= brackets[key][key2];
            }
        } else if (key != 'crit') {
            results['any'] *= brackets[key];
        }
    }
    for (const action of ACTION_SPECIFIC) {
        results[action] *= results['any'];
    }
    for (const key of Object.keys(results)) {
        $(`#${category}-${key}`).val(results[key]);
        if (baseResults) {
            $(`#${category}-relative-${key}`).val(results[key] / baseResults[key]);
        }
    }
    return results;
}
function calculateEffective() {
    const brackets = sumInputBrackets();
    const results = calculateEffectivePerCategory('base', brackets);
    for (const category of Object.keys(DRAGON_AURA)) {
        calculateEffectivePerCategory(category, brackets, results);
    }
}
window.onload = function () {
    makeEffectiveOutputs('base');
    for (const mod of MODIFIERS) {
        const modKey = `${mod[0]} - ${mod[1]}`;
        const modHolder = makeModifierItem(mod[0], mod[1], mod[2], mod[3], mod[4]);
        $('#modifiers').append(modHolder);
    }
    for (const category of Object.keys(DRAGON_AURA)) {
        appendDragonAuraEntry(category, DRAGON_AURA[category]);
    }
    setTimeout(calculateEffective, 200);
}