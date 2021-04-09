// const APP_URL = 'http://127.0.0.1:5000/';
const APP_URL = 'http://localhost:5000/';
// const APP_URL = 'https://wildshinobu.pythonanywhere.com/';
const BASE_SIM_T = 180;
const BASE_TEAM_DPS = 50000;
const WEAPON_TYPES = ['sword', 'blade', 'dagger', 'axe', 'lance', 'bow', 'wand', 'staff', 'gun'];
const DEFAULT_SHARE = 'Ranzal';
const DEFAULT_SHARE_ALT = 'Curran';
const SIMULATED_BUFFS = ['str_buff', 'def_down', 'critr', 'critd', 'doublebuff_interval', 'count', 'dprep', 'echo'];
const AFFLICT_COLORS = {
    poison: 'darkslateblue',
    paralysis: 'goldenrod',
    burn: 'orangered',
    blind: 'darkslategray',
    bog: 'dodgerblue',
    stun: 'gold',
    freeze: 'dodgerblue',
    sleep: 'slategray',
    frostbite: 'deepskyblue',
    flashburn: 'sandybrown',
    shadowblight: 'darkorchid',
    stormlash: 'olivedrab',
    scorchrend: 'coral'
};
const GITHUB_COMMIT_LOG = 'https://api.github.com/repos/dl-stuff/dl/commits?page=1'
let PIC_INDEX = null;

function populateAdvSelect(data) {
    let options = [];
    for (let d of Object.keys(data)) {
        options.push(
            $('<option>' + data[d].fullname + '</option>')
                .attr({ id: 'adv-' + d, value: d })
                .data('variants', data[d].variants)
        );
    }
    options.sort((a, b) => {
        if (a[0].innerText < b[0].innerText) return -1;
        if (a[0].innerText > b[0].innerText) return 1;
        return 0;
    });
    $('#input-adv').empty();
    $('#input-adv').append(options);
}
function populateVariantSelect(data) {
    $('#input-variant').empty();
    if (data.length === 0) {
        $('#input-variant-group').hide();
        return
    } else {
        $('#input-variant-group').show();
    }
    let options = [$('<option>Default</option>').attr({ id: 'variant-Default', value: null })];
    for (let d of data) {
        options.push(
            $('<option>' + d + '</option>')
                .attr({ id: 'variant-' + d, value: d })
        );
    }
    $('#input-variant').append(options);
}
function populateSelect(id, data, allowNone) {
    const t = id.split('-')[1];
    let options = [];
    if (allowNone) {
        options.push(
            $('<option></option>')
                .attr({ id: t + '-None', value: '' })
        );
    }
    for (let d of Object.keys(data)) {
        options.push(
            $('<option>' + data[d] + '</option>')
                .attr({ id: t + '-' + d, value: d })
        );
    }
    options.sort((a, b) => {
        if (a[0].innerText === 'Gold Fafnir') return -2;
        if (a[0].innerText < b[0].innerText) return -1;
        if (a[0].innerText > b[0].innerText) return 1;
        return 0;
    });
    $(id).empty();
    $(id).append(options);
}
function getIcon(qual, css) {
    return $('<img/>').attr({ src: `/dl-sim/pic/${PIC_INDEX[qual].icon}`, class: css !== undefined ? `slot-icon ${css}` : 'slot-icon' });
}
function slotsTextFmt(result) {
    return `[${PIC_INDEX[result.drg].name}][${PIC_INDEX[result.wep].name}][${result.wps.map((wp) => PIC_INDEX[wp].name).join('+')}][${result.coabs.map((coab) => PIC_INDEX[coab].name).join('|')}][${result.share.map((ss, i) => `S${i + 3}:${PIC_INDEX[ss].name}`).join('|')}]`;
}
function makeVisualResultItem(result) {
    const visualResult = $('<div></div>').attr({ class: 'test-result-item' });
    const iconRow = $('<h4 class="test-result-slot-grid"></h4>');
    const charaDiv = $('<div></div>');
    charaDiv.append(getIcon(result.adv, "character"));
    iconRow.append(charaDiv);
    iconRow.append(`<div>${PIC_INDEX[result.adv].name}</div > `);
    const iconDiv = $('<div></div>');
    iconDiv.append(getIcon(result.drg, "dragon"));
    iconDiv.append(getIcon(result.wep, "weapon"));
    for (const wp of result.wps) {
        iconDiv.append(getIcon(wp, "amulet"));
    }
    if (result.coabs.length > 0) {
        iconDiv.append(' | ');
    }
    for (const coab of result.coabs) {
        iconDiv.append(getIcon(coab, "coab"));
    }
    iconDiv.append(' | ');
    for (const ss of result.share) {
        iconDiv.append(getIcon(ss, "skillshare"));
    }
    iconRow.append(iconDiv);
    visualResult.append(iconRow);

    const metaRow = $('<h6>DPS:</h6>');
    const totalDPS = $(`<span class="dps-num">${result.dps}</span>`).data('total', result.dps);
    metaRow.append(totalDPS);
    metaRow.append(` - ${Math.round(result.real * 100) / 100}s`);
    if (result.stats) {
        metaRow.append(' |');
        for (const stat in result.stats) {
            const value = result.stats[stat];
            metaRow.append(`<img src="/dl-sim/pic/icons/${stat}.png" class="stat-icon"/>`);
            metaRow.append(value);
        }
    }
    if (result.cond) {
        metaRow.append(' | ');
        metaRow.append(result.cond);
    }
    if (result.comment) {
        if (result.cond) {
            metaRow.append(' | ');
        }
        metaRow.append(result.comment);
    }
    metaRow.append('<br/>');
    metaRow.append(slotsTextFmt(result));
    visualResult.append(metaRow);

    const DPSRow = $('<div></div>').attr({ class: 'result-bar' });

    for (const sliceInfo of result.slices) {
        const slice = sliceInfo[0];
        const value = sliceInfo[1];
        const dmgTxt = `${slice}: ${Math.floor(value)}`;
        const dmgSlice = $('<a>' + dmgTxt + '</a>')
            .data('dmg', value)
            .addClass('result-slice')
            .addClass('c-' + slice.split('_')[0])
            .css('width', 0)
            .attr({
                'data-toggle': 'tooltip',
                'data-placement': 'top',
                'title': dmgTxt
            }).tooltip();
        DPSRow.append(dmgSlice);
    }
    const teamSlice = $('<a>team</a>')
        .data('dmg', 0)
        .addClass('team-result-slice')
        .addClass('c-team')
        .css('width', 0)
        .attr({
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'team'
        }).tooltip();
    DPSRow.append(teamSlice);
    visualResult.append(DPSRow);
    visualResult.data("team", result.team);

    return visualResult
}
function makeTextResultItem(result) {
    let copyText = `**${result.adv.name} ${result.real}s**\n${slotsTextFmt(result)}`;
    copyText += '```';
    copyText += `DPS: ${result.dps} `;
    if (result.team > 0) {
        copyText += `team:${result.team} `;
    }
    if (result.stats) {
        copyText += `(${Object.keys(result.stats).map((stat) => `${stat}:${result.stats[stat]}`).join(', ')})`;
    }
    if (result.cond) {
        copyText += '\n';
        copyText += result.cond;
    }
    if (result.comment) {
        if (result.cond) {
            copyText += ' | ';
        } else {
            copyText += '\n';
        }
        copyText += result.comment;
    }
    copyText += '\n';
    copyText += result.slices.map((sliceInfo) => `${sliceInfo[0]}: ${sliceInfo[1]}`).join('|')
    copyText += '```';
    return $('<textarea>' + copyText + '</textarea>').attr({ class: 'copy-txt', rows: (copyText.match(/\n/g) || [0]).length + 1 });
}
function trimAcl(acl_str) {
    if (typeof acl_str === 'string' || acl_str instanceof String) {
        return $.trim(acl_str.replace(new RegExp(/[\n] +/, 'g'), '\n'));
    } else {
        return acl_str.join('\n');
    }
}
function getUrlVars() {
    let vars = {};
    window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        vars[key] = value;
    });
    return vars;
}
function updateUrl(urlVars) {
    if (urlVars && urlVars.conf) {
        history.replaceState(null, '', `${location.pathname}?conf=${urlVars.conf}`);
    } else {
        history.replaceState(null, '', location.pathname);
    }
}
function readWpList() {
    return [...$('.input-wp > div > select').map((_, v) => {
        const val = $(v).val();
        if (val) { return val; }
    })];
}
function serConf(no_conf) {
    let requestJson = {
        'adv': $('#input-adv').val(),
        'dra': $('#input-dra').val(),
        'wep': $('#input-wep').val()
    }
    const variant = $('#input-variant').val();
    if (variant && variant !== 'Default') {
        requestJson['variant'] = variant;
    }
    const wplist = readWpList();
    if (wplist) {
        requestJson['wp'] = wplist;
    }
    requestJson['share'] = readSkillShare();
    requestJson['coab'] = readCoabList();
    const t = $('#input-t').val();
    if (!isNaN(parseInt(t))) {
        requestJson['t'] = parseInt(t);
    }
    const afflict_res = readResistDict();
    if (afflict_res != null) {
        requestJson['afflict_res'] = afflict_res;
    }
    if ($('#input-specialmode').val()) {
        requestJson['specialmode'] = $('#input-specialmode').val();
    }
    if ($('#input-classbane').val()) {
        requestJson['classbane'] = $('#input-classbane').val();
    }
    if (!isNaN(parseInt($('#input-dumb').val()))) {
        requestJson['dumb'] = parseInt($('#input-dumb').val());
    }
    if (!isNaN(parseInt($('#input-hp').val()))) {
        requestJson['hp'] = parseInt($('#input-hp').val());
    }
    if ($('#input-edit-acl').prop('checked')) {
        requestJson['acl'] = $('#input-acl').val();
    } else {
        requestJson['acl'] = $('#input-acl').data('default_acl');
    }
    const sim_aff = readSimAfflic();
    if (sim_aff != null) {
        requestJson['sim_afflict'] = sim_aff;
    }
    const sim_buff = readSimBuff();
    if (sim_buff != null) {
        requestJson['sim_buff'] = sim_buff;
    }

    if (!no_conf) {
        const urlVars = { conf: btoa(JSON.stringify(requestJson)) };
        updateUrl(urlVars);
    }
    return requestJson;
}
function deserConf(confStr) {
    return JSON.parse(atob(confStr));
}
function loadConf(conf, slots) {
    slots.adv.pref_wep = conf.wep;
    slots.adv.pref_dra = conf.dra;
    if (conf.wp) {
        slots.adv.pref_wp = conf.wp;
    }
    if (conf.coab) {
        slots.adv.pref_coab = conf.coab;
    }
    if (conf.share) {
        slots.adv.pref_share = conf.share;
    }
    if (conf.acl) {
        slots.adv.acl_alt = conf.acl;
    }
    if (conf.afflict_res) {
        slots.adv.afflict_res = conf.afflict_res
    }
    if (conf.teamdps) {
        $('#input-teamdps').val(conf.teamdps);
        localStorage.setItem('simc-teamdps', conf.teamdps);
    }
    for (const key of ['t', 'hp', 'specialmode', 'classbane']) {
        if (conf[key]) {
            $('#input-' + key).val(conf[key]);
        }
    }
    if (conf.sim_afflict) {
        for (const key of Object.keys(conf.sim_afflict)) {
            const res = $('#affliction-sim #input-sim-' + key);
            if (res) {
                res.val(conf.sim_afflict[key]);
            }
        }
    }
    if (conf.sim_buff) {
        for (const key of Object.keys(conf.sim_buff)) {
            const res = $('#input-sim-buff' + key);
            if (res) {
                res.val(conf.sim_buff[key]);
            }
        }
    }
    return slots;
}
function populateSkillShare(skillshare) {
    $('#input-ss3').empty();
    $('#input-ss3').append($('<option>Weapon</option>')
        .attr({ id: 'ss3-Weapon', value: '' }));
    $('#input-ss4').empty();
    for (const t of ['ss3', 'ss4']) {
        let options = [];
        for (const ss in skillshare) {
            const ss_data = skillshare[ss];
            const ss_repr = ss_data.fullname + '\t(S' + ss_data['s'] + ': ' + ss_data['sp'] + ' SP, ' + ss_data['cost'] + ' Cost)';
            options.push($('<option>' + ss_repr + '</option>')
                .attr({ id: t + '-' + ss, value: ss }))
        }
        options.sort((a, b) => {
            if (a[0].innerText < b[0].innerText) return -1;
            if (a[0].innerText > b[0].innerText) return 1;
            return 0;
        })
        $('#input-' + t).append(options);
    }
}
function loadAdvWPList() {
    let selectedAdv = 'Patia';
    let selectedVariant = null;
    if (localStorage.getItem('selectedAdv')) {
        selectedAdv = localStorage.getItem('selectedAdv');
    }
    const urlVars = getUrlVars();
    if (urlVars) {
        if (urlVars.conf) {
            const conf = deserConf(urlVars.conf);
            selectedAdv = conf.adv;
        } else if (urlVars.adv_name) {
            selectedAdv = urlVars.adv_name;
            selectedVariant = urlVars.variant;
        }
        updateUrl(urlVars);
    }
    $.ajax({
        url: APP_URL + 'simc_adv_wp_list',
        dataType: 'text',
        type: 'post',
        contentType: 'application/json',
        success: function (data, textStatus, jqXHR) {
            if (jqXHR.status == 200) {
                const advwp = JSON.parse(data);
                populateAdvSelect(advwp.adv);
                $('#adv-' + selectedAdv).prop('selected', true);
                populateVariantSelect($('#adv-' + selectedAdv).data('variants'));
                if (selectedVariant != null) {
                    $('#variant-' + selectedVariant).prop('selected', true);
                }
                populateSelect('#input-wp1', advwp.wyrmprints.formA);
                populateSelect('#input-wp2', advwp.wyrmprints.formA);
                populateSelect('#input-wp3', advwp.wyrmprints.formA);
                populateSelect('#input-wp4', advwp.wyrmprints.formB);
                populateSelect('#input-wp5', advwp.wyrmprints.formB);
                populateSelect('#input-wp6', advwp.wyrmprints.formC, true);
                populateSelect('#input-wp7', advwp.wyrmprints.formC, true);
                populateSkillShare(advwp.skillshare);
                clearResults();
                loadAdvSlots(true, true);
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            $('#test-error').html('Failed to load initial data');
        }
    });
}
function selectSkillShare(basename, pref_share) {
    for (const t of ['ss3', 'ss4']) {
        $('#input-' + t + ' > option').prop('disabled', false);
        $('#' + t + '-' + basename).prop('disabled', true);
    }
    switch (pref_share.length) {
        case 1:
            $('#ss3-Weapon').prop('selected', true);
            $('#ss4-' + pref_share[0]).prop('selected', true);
            break;
        case 2:
            $('#ss3-' + pref_share[0]).prop('selected', true);
            $('#ss4-' + pref_share[1]).prop('selected', true);
            break;
        default:
            $('#ss3-Weapon').prop('selected', true);
            if (basename === DEFAULT_SHARE) {
                $('#ss4-' + DEFAULT_SHARE_ALT).prop('selected', true);
            } else {
                $('#ss4-' + DEFAULT_SHARE).prop('selected', true);
            }
            break;
    }
}
function readEquipCondition() {
    return {
        'aff': $('#input-aff').val(),
        'sit': $('#input-sit').val(),
        'mono': $('#input-mono').prop('checked') ? "MONO" : "ANY",
        'opt': $('#input-opt').val()
    }
}
function setSlotUI(ui) {
    if (ui.afflict_res) {
        for (const key in ui.afflict_res) {
            const res = ui.afflict_res[key];
            if (res > 100) {
                $('#input-res-' + key).val(res);
            } else {
                $('#input-res-' + key).val('');
                $('#input-res-' + key).attr('placeholder', res);
            }
        }
    }
    if (ui.sim_afflict) {
        for (const aff in ui.sim_afflict) {
            $('#input-sim-' + aff).val(ui.sim_afflict[aff]);
        }
    }
    for (const selKey of ['specialmode', 'aff', 'sit', 'opt']) {
        if (ui[selKey]) {
            $(`#input-${selKey}-${ui[selKey]}`).prop('selected', true);
        }
    }
}
function loadAdvSlots(no_conf, default_equip) {
    if ($('#input-adv').val() == '') {
        return false;
    }
    toggleInputDisabled(true);
    const urlVars = getUrlVars();
    let conf = undefined;
    if (urlVars.conf) {
        conf = deserConf(urlVars.conf);
    }
    const adv_name = $('#input-adv').val();
    localStorage.setItem('selectedAdv', adv_name);
    const requestJson = {
        'adv': adv_name
    };
    if (!default_equip) {
        requestJson['equip'] = readEquipCondition();
        const variant = $('#input-variant').val();
        if (variant && variant !== 'Default') {
            requestJson['variant'] = variant;
        }
    }
    const t = $('#input-t').val();
    if (!isNaN(parseInt(t))) {
        requestJson['t'] = t;
    };
    $.ajax({
        url: APP_URL + 'simc_adv_slotlist',
        dataType: 'text',
        type: 'post',
        contentType: 'application/json',
        data: JSON.stringify(requestJson),
        success: function (data, textStatus, jqXHR) {
            if (jqXHR.status == 200) {
                let slots = JSON.parse(data);
                if (slots.hasOwnProperty('error')) {
                    $('#test-error').html('Error: ' + slots.error);
                } else {
                    $('#test-error').empty();
                    populateSelect('#input-wep', slots.weapons);
                    populateSelect('#input-dra', slots.dragons);
                    buildCoab(slots.coabilities, slots.adv.basename, slots.adv.wt);

                    const urlVars = getUrlVars();
                    if (urlVars.conf) { slots = loadConf(conf, slots); }

                    $('#wep-' + slots.adv.pref_wep).prop('selected', true);
                    $('#dra-' + slots.adv.pref_dra).prop('selected', true);
                    for (let i = 0; i < 7; i++) {
                        if (slots.adv.pref_wp[i]) {
                            $(`#wp${i + 1}-` + slots.adv.pref_wp[i]).prop('selected', true);
                        } else {
                            $(`#wp${i + 1}-None`).prop('selected', true);
                        }
                    }

                    for (const c of slots.adv.pref_coab) {
                        const check = $("input[id$='-" + c + "']");
                        if (check.length) {
                            check.prop('checked', true);
                            coabSelection(1, true);
                        }
                    }
                    selectSkillShare(slots.adv.basename, slots.adv.pref_share);
                    const acl = trimAcl(slots.adv.acl);
                    $('#input-acl').data('default_acl', acl);
                    $('#input-acl').removeData('alternate_acl');
                    $('#input-acl').blur();
                    const acl_check = Boolean(slots.adv.acl_alt && slots.adv.acl_alt != acl);
                    $('#input-edit-acl').prop('checked', acl_check);
                    $('#input-acl').prop('disabled', !acl_check);
                    if (slots.adv.acl_alt) {
                        const acl_alt = trimAcl(slots.adv.acl_alt);
                        $('#input-acl').data('alternate_acl', acl_alt);
                        $('#input-acl').val(acl_alt);
                    } else {
                        $('#input-acl').val(acl);
                    }
                    $('#input-toggle-affliction').prop('checked', false);
                    $('.input-wp > div > select').prop('disabled', false);
                    $('#input-edit-acl').prop('disabled', false);
                    $('input.coab-check').prop('disabled', false);

                    if (!urlVars.conf) {
                        const simAff = $('#affliction-sim > div > input[type="text"]');
                        simAff.each(function (idx, res) { $(res).val(''); });
                    }
                    if (slots.ui) {
                        setSlotUI(slots.ui);
                    }
                    runAdvTest(no_conf);
                }
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            $('#test-error').html('Failed to load adventurer');
            toggleInputDisabled(false);
        }
    });
}
function readResistDict() {
    let resists = {};
    const resistList = $('#affliction-resist input[type="text"]');
    if (resistList.length === 0) {
        return null;
    } else {
        resistList.each(function (idx, res) {
            const resVal = parseInt($(res).val());
            if (!isNaN(resVal) && resVal >= 0) {
                const parts = $(res).attr('id').split('-');
                resists[parts[parts.length - 1]] = resVal;
            }
        });
        if ($.isEmptyObject(resists)) {
            return null;
        }
        return resists;
    }
}
function checkCoabSelection(e) {
    const add = $(e.target).prop('checked') ? 1 : -1
    coabSelection(add);
}
function coabSelection(add, debounce) {
    const count = $('#input-coabs').data('selected') + add;
    const max = $('#input-coabs').data('max');
    if (count >= max) {
        if (debounce) {
            setTimeout(function () { $('input:not(:checked).coab-check').prop('disabled', true); }, 50);
        } else {
            $('input:not(:checked).coab-check').prop('disabled', true);
        }
        // const self = $('#input-coabs').data('self');
        // if (self) {
        //     if (debounce) {
        //         setTimeout(function () { $("input[id$='-" + self + "']").prop('disabled', false); }, 55);
        //     } else {
        //         $("input[id$='-" + self + "']").prop('disabled', false);
        //     }
        // }
    } else {
        $('.coab-check').prop('disabled', false);
    }

    if (add == 0) {
        const selfcoab = $('#input-coabs').data('selfcoab');
        $('#coab-' + selfcoab).prop('disabled', true);
        $('#coab-' + selfcoab).prop('checked', true);
    }

    $('#input-coabs').data('selected', count);
}

function buildCoab(coab, basename, weapontype) {
    $('#input-coabs > div').empty();
    $('#input-coabs').data('max', 3);
    let found_basename = null;
    $('#input-coabs').data('selected', 0);
    for (const k in coab) {
        const cid = 'coab-' + k;
        const wrap = $('<div></div>').addClass('custom-control custom-checkbox custom-control-inline');
        const check = $('<input>').addClass('custom-control-input').prop('type', 'checkbox').prop('id', cid);
        const kcoab = coab[k];
        const fullname = kcoab[0];
        const ex = kcoab[1];
        const chain = kcoab[2];
        check.data('name', k);
        check.data('ex', ex);
        check.data('chain', chain);
        check.change(checkCoabSelection);
        if (k == basename) {
            check.prop('disabled', true);
            check.prop('checked', true);
            found_basename = ex;
            $('#input-coabs').data('selfcoab', basename);
        } else {
            check.addClass('coab-check');
        }
        const label = $(`<label>${fullname}</label>`).addClass('custom-control-label').prop('for', cid);
        wrap.append(check);
        wrap.append(label);
        if (chain) {
            wrap.prop('title', `${ex}-${chain}`);
        } else {
            wrap.prop('title', ex);
        }
        if (WEAPON_TYPES.includes(ex)) {
            $('#input-coabs-' + ex).append(wrap);
        } else {
            $('#input-coabs-other').append(wrap);
        }
    }
    const wt = weapontype.charAt(0).toUpperCase() + weapontype.slice(1);
    let check = $('#coab-' + wt);
    if (found_basename) {
        check = $('#coab-' + found_basename);
    } else {
        $('#input-coabs').data('selfcoab', wt);
    }
    check.prop('disabled', true);
    check.prop('checked', true);
    check.removeClass('coab-check');
}
function readCoabList() {
    const coabList = $('input:checked.coab-check');
    if (coabList.length === 0) {
        return [];
    } else {
        const coabilities = [];
        coabList.each(function (idx, res) {
            coabilities.push($(res).data('name'));
        });
        return coabilities;
    }
}
function readSkillShare() {
    const skillShare = [];
    if ($('#input-ss3').val() != '') {
        skillShare.push($('#input-ss3').val());
    }
    if ($('#input-ss4').val() != '') {
        skillShare.push($('#input-ss4').val());
    }
    if (skillShare.length === 0) {
        return null;
    } else {
        return skillShare;
    }
}
function readSimAfflic() {
    let simAff = {};
    const affList = $('#affliction-sim > div > input[type="text"]');
    if (affList.length === 0) {
        return null;
    } else {
        affList.each(function (idx, res) {
            const resVal = parseInt($(res).val());
            if (!isNaN(resVal) && resVal > 0) {
                const parts = $(res).attr('id').split('-');
                simAff[parts[parts.length - 1]] = resVal;
            }
        });
        if ($.isEmptyObject(simAff)) {
            return null;
        }
        return simAff;
    }
}
function readSimBuff() {
    let simBuff = {};
    for (let key of SIMULATED_BUFFS) {
        const buff_value = $('#input-sim-buff-' + key).val();
        if (!isNaN(parseFloat(buff_value))) {
            simBuff[key] = parseFloat(buff_value);
        }
    }
    if ($.isEmptyObject(simBuff)) {
        return null;
    }
    return simBuff;
}
function toggleInputDisabled(state) {
    $('input').prop('disabled', state);
    if ($('#input-edit-acl').prop('checked')) {
        $('#input-acl').prop('disabled', state);
    }
    $('select').prop('disabled', state);
    if (!state) {
        coabSelection(0);
    }
}
let graphData = null;
function windows(data) {
    const result = [{ x: 0, y: 0 }];
    const thresh = 5;
    for (let obj of data) {
        let sum = 0;
        for (let sobj of data) {
            if (sobj.x > obj.x + thresh) { break; }
            if (sobj.x < obj.x - thresh) { continue; }
            sum += sobj.y;
        }
        result.push({ x: Math.round(obj.x * 1000) / 1000, y: Math.round(sum / (thresh * 2)) });
    }
    return result;
}
function scaled(data, scale) {
    scale = scale || 1;
    const result = [{ x: 0, y: 0 }];
    let prev = 0;
    for (let obj of data) {
        result.push({ x: Math.round(obj.x * 1000) / 1000, y: prev });
        prev = Math.round(obj.y * scale);
        result.push({ x: Math.round(obj.x * 1000) / 1000, y: prev });
    }
    return result;
}
function makeDataset(label, data, color) {
    return {
        label: label,
        data: data,
        borderColor: color,
        backgroundColor: 'rgb(192,192,192, 0.3)',
        showLine: true,
        // fill: false,
        pointRadius: 0.5,
        lineTension: 0,
    }
}
function makeGraph(ctx, datasets, ystep) {
    return new Chart(ctx, {
        type: 'line',
        data: { datasets: datasets },
        options: {
            scales: {
                xAxes: [{
                    type: 'linear',
                    ticks: {
                        beginAtZero: true,
                        stepSize: 1,
                        suggestedMin: 0,
                        suggestedMax: graphData.duration
                    },
                }],
                yAxes: [{
                    type: 'linear',
                    ticks: {
                        beginAtZero: true,
                        stepSize: ystep
                    },
                }]
            },
            animation: { duration: 0 },
            // tooltips: { enabled: false }
        }
    })
}
function killGraph(graph) {
    if (graph) { graph.destroy(); }
}
let simcDamageGraph = null;
let simcDoublebuffGraph = null;
let simcUptimeGraph = null;
function populateAllGraphs() {
    if (!graphData) {
        return;
    }
    const tdps = $('#input-teamdps').val();
    killGraph(simcDamageGraph);
    const datasets = [makeDataset('Damage', windows(graphData.dmg), 'mediumslateblue')];
    if (Object.keys(graphData.team).length > 1) {
        datasets.push(makeDataset('Team', scaled(graphData.team, tdps), 'seagreen'));
    }
    simcDamageGraph = makeGraph('damage-graph', datasets, 5000);

    killGraph(simcDoublebuffGraph);
    killGraph(simcUptimeGraph);
    if (graphData.doublebuff) {
        $('#doublebuff-graph').show();
        simcDoublebuffGraph = makeGraph('doublebuff-graph', [makeDataset('Doublebuff', scaled(graphData.doublebuff), 'steelblue')], 1);
    } else {
        $('#doublebuff-graph').hide();
    }

    const affUptimeDatasets = [];
    for (const aff of Object.keys(AFFLICT_COLORS)) {
        if (graphData[aff]) {
            affUptimeDatasets.push(makeDataset(aff.slice(0, 1).toUpperCase() + aff.slice(1), scaled(graphData[aff]), AFFLICT_COLORS[aff]));
        }
    }
    if (affUptimeDatasets.length > 0) {
        $('#uptime-graph').show();
        simcUptimeGraph = makeGraph('uptime-graph', affUptimeDatasets, 1);
    } else {
        $('#uptime-graph').hide();
    }
}
function clearAllGraphs() {
    killGraph(simcDamageGraph);
    killGraph(simcDoublebuffGraph);
    killGraph(simcUptimeGraph);
}
function runAdvTest(no_conf) {
    if ($('#input-adv').val() == '') {
        return false;
    }
    toggleInputDisabled(true);
    $('#test-error').empty();
    $('div[role="tooltip"]').remove();
    const requestJson = serConf(no_conf);
    $.ajax({
        url: APP_URL + 'simc_adv_test',
        dataType: 'text',
        type: 'post',
        contentType: 'application/json',
        data: JSON.stringify(requestJson),
        success: function (data, textStatus, jqXHR) {
            if (jqXHR.status == 200) {
                const res = JSON.parse(data);
                if (res.hasOwnProperty('error')) {
                    $('#test-error').html('Error: ' + res.error);
                } else {
                    $('#test-results').prepend(makeVisualResultItem(res.test_output));
                    $('#copy-results').prepend(makeTextResultItem(res.test_output));
                    const logs = ['dragon', 'misc', 'summation', 'action', 'timeline'].map(key => {
                        if (res.logs[key] !== undefined && res.logs[key] !== "") {
                            return res.logs[key];
                        } else {
                            return false;
                        }
                    }).filter(l => (l));
                    $('#damage-log').html(logs.join('<hr class="log-divider">'));
                    graphData = res.chart;
                    graphData.duration = requestJson['t'];
                    updateTeamdps();
                }
            }
            toggleInputDisabled(false);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            $('#test-error').html('Failed to run damage simulation');
            toggleInputDisabled(false);
        }
    });
}
function editAcl() {
    $('#input-acl').prop('disabled', !$(this).prop('checked'));
    if ($(this).prop('checked')) {
        $('#input-acl').prop('disabled', false);
        const altAcl = $('#input-acl').data('alternate_acl');
        if (altAcl) {
            $('#input-acl').val(altAcl);
        }
    } else {
        $('#input-acl').data('alternate_acl', $('#input-acl').val());
        $('#input-acl').prop('disabled', true);
        $('#input-acl').val($('#input-acl').data('default_acl'));
    }
}
function debounce(func, interval) {
    let lastCall = -1;
    return function () {
        clearTimeout(lastCall);
        lastCall = setTimeout(function () {
            func.apply();
        }, interval);
    };
}
function setDisplay(displayMode) {
    if (displayMode == 'Visual') {
        $('#copy-results').css('display', 'block');
        $('#test-results').css('display', 'none');
        $('#display-mode').html('Visual Display');
        localStorage.setItem('displayMode', displayMode);
    } else if (displayMode == 'Markdown') {
        $('#copy-results').css('display', 'none');
        $('#test-results').css('display', 'block');
        $('#display-mode').html('Text Display');
        localStorage.setItem('displayMode', displayMode);
    }
}
function toggleDisplay() {
    if (localStorage.getItem('displayMode') == 'Markdown') {
        setDisplay('Visual');
    } else {
        setDisplay('Markdown');
    }
}
function clearResults() {
    $('#test-results').empty();
    $('#copy-results').empty();
    $('#test-error').empty();
    $('#input-t').val(BASE_SIM_T);
    if (localStorage.getItem('simc-teamdps')) {
        $('#input-teamdps').val(localStorage.getItem('simc-teamdps'));
    } else {
        $('#input-teamdps').val(BASE_TEAM_DPS);
        localStorage.setItem('simc-teamdps', BASE_TEAM_DPS);
    }
    // $('#input-missile').val('');
    $('#input-hp').val('');
    const resistList = $('#affliction-resist input[type="text"]');
    resistList.each(function (idx, res) { $(res).val(''); });
    const simAff = $('#affliction-sim > div > input[type="text"]');
    simAff.each(function (idx, res) { $(res).val(''); });
    $('input:checked.coab-check').prop('check', false);
    for (let key of SIMULATED_BUFFS) {
        $('#input-sim-buff-' + key).val('');
    }
    // $('#input-conditions').empty();
    $('#input-specialmode').val('');
    $('#input-classbane').val('');
    $('#input-dumb').val('');
    // $('#input-mono').prop('checked', false);
    $('#input-toggle-affliction').prop('checked', false);
    clearAllGraphs();
}
function resetTest() {
    updateUrl();
    clearResults();
    populateVariantSelect($('#adv-' + $('#input-adv').val()).data('variants'));
    loadAdvSlots(true, true);
}
function weaponSelectChange() {
    const weapon = $('#input-wep').val();
    if (weapon.startsWith('Agito') || weapon.startsWith('UnreleasedAgito')) {
        $('#input-edit-acl').prop('checked', true);
        $('#input-acl').prop('disabled', false);
        const acl = $('#input-acl').val().split('\n');
        let new_acl = '`s3, not buff(s3)\n';
        for (const line of acl) {
            if (!line.startsWith('`s3')) {
                new_acl += line + '\n';
            }
        }
        $('#input-acl').val(new_acl);
    } else {
        $('#input-edit-acl').prop('checked', false);
        $('#input-acl').prop('disabled', true);
        $('#input-acl').val($('#input-acl').data('default_acl'));
    }
}
function loadGithubCommits() {
    $.ajax({
        url: GITHUB_COMMIT_LOG,
        dataType: 'text',
        type: 'get',
        contentType: 'application/json',
        success: function (data, textStatus, jqXHR) {
            if (jqXHR.status == 200) {
                const commits = JSON.parse(data);
                for (const commit of commits) {
                    const c = commit.commit; var startDate = new Date();
                    const authorTime = moment(c.author.date);
                    const entry = $('<a></a>').attr({ class: 'commit-entry', href: commit.html_url });
                    entry.append($('<span>' + commit.author.login + '</span>').attr({ class: 'commit-author' }));
                    entry.append($('<span> - ' + authorTime.fromNow() + '</span>').attr({ class: 'commit-time' }));
                    entry.append($('<div>' + c.message + '</div>').attr({ class: 'commit-message' }));
                    $('#changelog').append(entry);
                }
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            // $('#changelog').html('Failed to load github commits');
        }
    });
}
function updateTeamdps() {
    const tdps = $('#input-teamdps').val();
    if (!$('#input-teamdps').data('original')) {
        localStorage.setItem('simc-teamdps', tdps);
    }
    $('.test-result-item').each((_, ri) => {
        const team_p = $(ri).data('team');
        const team_v = tdps * team_p;
        const dps_num = $(ri).find('.dps-num')[0];
        const new_total = $(dps_num).data('total') + team_v;
        $(dps_num).html(Math.ceil(new_total));
        let others = 0;
        $(ri).find('.result-slice').each((_, rs) => {
            const portion = (team_v > 0) ? Math.ceil(990 * ($(rs).data('dmg') / new_total)) / 10 : Math.floor(990 * ($(rs).data('dmg') / new_total)) / 10;
            others += portion;
            $(rs).css('width', portion + '%');
        });
        if (team_p == 0) { return; }
        const tdps_txt = 'team: ' + Math.ceil(team_v) + ' (+' + Math.round(team_p * 100) + '%)';
        const trs = $(ri).find('.team-result-slice')[0];
        const portion = 100 - others;
        $(trs).css('width', portion + '%');
        $(trs).html(tdps_txt)
        $(trs).attr('data-original-title', tdps_txt);
    });
}
function reloadSlots() {
    updateUrl();
    loadAdvSlots(true);
}
function toggleAffRes() {
    const newVal = $(this).prop('checked') ? 999 : '';
    $('#affliction-resist input[type="text"]').each(function (idx, res) { $(res).val(newVal); });
}
window.onload = function () {
    PIC_INDEX = $.getJSON("/dl-sim/pic/index.json", function (data) {
        PIC_INDEX = data;
    });

    $('#input-adv').change(debounce(resetTest, 100));
    for (const ekey of ["variant", "opt", "aff", "sit", "mono"]) {
        $(`#input-${ekey}`).change(debounce(reloadSlots, 100));
    }
    $('#run-test').click(debounce(runAdvTest, 100));
    if (!localStorage.getItem('displayMode')) {
        localStorage.setItem('displayMode', 'Markdown');
    }
    setDisplay(localStorage.getItem('displayMode'));
    $('#display-mode').click(toggleDisplay);
    $('#clear-results').click(clearResults);
    $('#reset-test').click(resetTest);
    $('#input-edit-acl').change(editAcl);
    $('#input-toggle-affliction').change(toggleAffRes);
    $('#input-teamdps').change(updateTeamdps);
    // $('#input-wep').change(weaponSelectChange);
    clearResults();
    loadAdvWPList();
    loadGithubCommits();
    $('#simulationGraphBox').on('shown.bs.modal', populateAllGraphs);
}