// const APP_URL = 'http://127.0.0.1:5000/';
const APP_URL = 'https://wildshinobu.pythonanywhere.com/';
const BASE_SIM_T = 180;
const BASE_TEAM_DPS = 50000;
const WEAPON_TYPES = ['sword', 'blade', 'dagger', 'axe', 'lance', 'bow', 'wand', 'staff', 'gun'];
const RANGED = ['wand', 'bow', 'staff', 'gun'];
const DEFAULT_SHARE = 'Ranzal';
const DEFAULT_SHARE_ALT = 'Curran';
const SIMULATED_BUFFS = ['str_buff', 'def_down', 'critr', 'critd', 'doublebuff_interval', 'count', 'echo'];
const ELE_AFFLICT = {
    'flame': 'burn',
    'water': 'frostbite',
    'wind': 'poison',
    'light': 'paralysis',
    'shadow': 'poison'
}
const GITHUB_COMMIT_LOG = 'https://api.github.com/repos/dl-stuff/dl/commits?page=1'
function name_fmt(name) {
    return name.replace(/_/g, ' ').replace(/(?:^|\s)\S/g, function (a) { return a.toUpperCase(); });
}
const speshul = {
    Lily: 'https://cdn.discordapp.com/emojis/664261164208750592.png'
}

function slots_icon_fmt(data) {
    const adv = data[2];
    const img_urls = [];
    if (speshul.hasOwnProperty(data[1]) && Math.random() < 0.1) {
        img_urls.push('<img src="' + speshul[data[1]] + '" class="slot-icon character"/>');
    } else {
        img_urls.push('<img src="/dl-sim/pic/character/' + adv + '.png" class="slot-icon character"/>');
    }
    img_urls.push('<img src="/dl-sim/pic/dragon/' + data[7] + '.png" class="slot-icon dragon"/>');
    img_urls.push('<img src="/dl-sim/pic/weapon/' + data[9] + '.png" class="slot-icon weapon"/>');
    for (const w of Array(5).keys()) {
        img_urls.push('<img src="/dl-sim/pic/amulet/' + data[11 + w * 2] + '.png" class="slot-icon"/>');
    }
    img_urls.push(' | ');
    for (const c of Array(3).keys()) {
        const c_name = data[20 + c * 2];
        const c_icon = data[21 + c * 2];
        if (c_icon) {
            img_urls.push('<img src="/dl-sim/pic/character/' + c_icon + '.png" class="slot-icon coab unique"/>');
        } else if (c_name) {
            img_urls.push('<img src="/dl-sim/pic/coabs/' + c_name + '.png" class="slot-icon coab generic"/>');
        }
    }
    img_urls.push(' | ');
    if (data[27]) {
        img_urls.push('<img src="/dl-sim/pic/character/' + data[27] + '.png" class="slot-icon skillshare"/>');
    } else {
        img_urls.push('<img src="/dl-sim/pic/icons/weaponskill.png" class="slot-icon skillshare"/>');
    }
    img_urls.push('<img src="/dl-sim/pic/character/' + data[29] + '.png" class="slot-icon skillshare"/>');
    return img_urls;
}
function slots_text_format(data) {
    return `[${data[6]}][${data[8]}][${data[10]}+${data[12]}+${data[14]}+${data[16]}+${data[18]}][${data[20]}|${data[22]}|${data[24]}][S3:${data[26]}|S4:${data[28]}]`
}
function populate_select(id, data) {
    const t = id.split('-')[1];
    let options = [];
    for (let d of Object.keys(data)) {
        options.push(
            $('<option>' + data[d] + '</option>')
                .attr({ id: t + '-' + d, value: d })
        );
    }
    options.sort((a, b) => {
        if (a[0].innerText < b[0].innerText) return -1;
        if (a[0].innerText > b[0].innerText) return 1;
        return 0;
    })
    $(id).empty();
    $(id).append(options);
}
function stats_icon_fmt(stat_str) {
    if (!stat_str) {
        return [[], 0];
    }
    const stats = [];
    let team = 0;
    for (const part of stat_str.split(';')) {
        const subparts = part.split(':');
        const name = subparts[0];
        if (name === 'team') {
            team = parseFloat(subparts[1]);
        } else {
            const value = subparts[1];
            stats.push('<img src="/dl-sim/pic/icons/' + name + '.png" class="stat-icon"/>');
            stats.push(value);
        }
    }
    return [stats, parseFloat(team)];
}
function create_dps_bar(res_div, arr) {
    let copy_txt = '';
    const total = arr[0];
    let slots = ' ' + slots_text_format(arr);
    const cond = arr[30] || '';
    const comment = arr[31] || '';
    let cond_comment = [];
    let cond_comment_str = '';
    let cond_cpy_str = '';
    if (cond != undefined && !cond.startsWith('!')) {
        if (cond != '') {
            cond_comment.push(cond);
        }
        if (comment != '') {
            cond_comment.push(comment);
        }
        if (cond_comment.length > 0) {
            cond_comment_str = '<br/>' + cond_comment.join(' ');
            cond_cpy_str = '\n' + cond_comment.join(' ');
        }
    } else {
        slots = '';
    }
    let stat_str = arr[32] || '';
    const stats = stats_icon_fmt(stat_str);
    const stats_display = stats[0].join('');
    const team = stats[1];
    if (stat_str) { stat_str = ' (' + stat_str.replace(';', ', ') + ')'; }

    let total_dps = parseInt(arr[0]);

    res_div.data('team', team);
    const dpsnum = $('<span class="dps-num">' + total_dps + '</span>').data('total', total_dps);
    const dpshead = $('<h6>DPS:</h6>');
    dpshead.append(dpsnum);
    dpshead.append(slots + cond_comment_str + stats_display);
    res_div.append(dpshead);
    copy_txt += slots + '```DPS: ' + total + stat_str + cond_cpy_str + '\n';

    let res_bar = $('<div></div>').attr({ class: 'result-bar' });
    let damage_txt_arr = [];
    for (let i = 33; i < arr.length; i++) {
        const dmg = arr[i].split(':')
        if (dmg.length == 2) {
            const dmg_val = parseInt(dmg[1]);
            if (dmg_val > 0) {
                // const portion = 100 * (dmg_val / total_dps);
                let damage_txt = dmg[0] + ': ' + dmg[1];
                damage_txt_arr.push(damage_txt);
                const damage_slice = $('<a>' + damage_txt + '</a>')
                    .data('dmg', dmg_val)
                    .addClass('result-slice')
                    .addClass('c-' + dmg[0].split('_')[0])
                    .css('width', 0)
                    .attr({
                        'data-toggle': 'tooltip',
                        'data-placement': 'top',
                        'title': damage_txt
                    }).tooltip();
                res_bar.append(damage_slice);
            }
        }
    }
    const team_slice = $('<a>team</a>')
        .data('dmg', 0)
        .addClass('team-result-slice')
        .addClass('c-team')
        .css('width', 0)
        .attr({
            'data-toggle': 'tooltip',
            'data-placement': 'top',
            'title': 'team'
        }).tooltip();
    res_bar.append(team_slice);

    copy_txt += damage_txt_arr.join('|') + '```';
    // copy_txt += damage_txtBar.join('') + '```';
    res_div.append(res_bar);
    return copy_txt;
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
    return [...$('.input-wp > div > select').map((_, v) => $(v).val())];
}
function serConf(no_conf) {
    let requestJson = {
        'adv': $('#input-adv').val(),
        'dra': $('#input-dra').val(),
        // 'wep': $('#input-wep').val()
    }
    const wplist = readWpList();
    if (wplist) {
        requestJson['wp'] = wplist;
    }
    requestJson['share'] = readSkillShare();
    requestJson['coab'] = readCoabList();
    const t = $('#input-t').val();
    if (!isNaN(parseInt(t))) {
        requestJson['t'] = t;
    }
    const afflict_res = readResistDict();
    if (afflict_res != null) {
        requestJson['afflict_res'] = afflict_res;
    }
    // if (!isNaN(parseInt($('#input-teamdps').val()))) {
    //     const dps = $('#input-teamdps').val();
    //     requestJson['teamdps'] = dps;
    //     localStorage.setItem('teamdps', dps);
    // }
    // if (!isNaN(parseInt($('#input-missile').val()))) {
    //     requestJson['missile'] = $('#input-missile').val();
    // }
    if (!isNaN(parseInt($('#input-dragonbattle').val()))) {
        requestJson['dragonbattle'] = $('#input-dragonbattle').val();
    }
    if (!isNaN(parseInt($('#input-hp').val()))) {
        requestJson['hp'] = $('#input-hp').val();
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
    const condition = readConditionList();
    if (condition !== null) {
        requestJson['condition'] = condition;
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
    // slots.adv.pref_wep = conf.wep;
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
        localStorage.setItem('teamdps', conf.teamdps);
    }
    for (const key of ['t', 'hp', 'dragonbattle']) {
        if (conf[key]) {
            $('#input-' + key).val(conf[key]);
        }
    }
    if (conf.sim_afflict) {
        for (const key of Object.keys(conf.sim_afflict)) {
            const res = $('#affliction-sim > div > #input-sim-' + key);
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
    let selectedAdv = 'Euden';
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
                populate_select('#input-adv', advwp.adv);
                $('#adv-' + selectedAdv).prop('selected', true);
                populate_select('#input-wp1', advwp.wyrmprints.gold);
                populate_select('#input-wp2', advwp.wyrmprints.gold);
                populate_select('#input-wp3', advwp.wyrmprints.gold);
                populate_select('#input-wp4', advwp.wyrmprints.silver);
                populate_select('#input-wp5', advwp.wyrmprints.silver);
                populateSkillShare(advwp.skillshare);
                clearResults();
                loadAdvSlots(true);
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
function loadAdvSlots(no_conf, set_equip) {
    if ($('#input-adv').val() == '') {
        return false;
    }
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
    if (set_equip) {
        requestJson['equip'] = $('#input-equip').val();
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
                    populate_select('#input-wep', slots.weapons);
                    populate_select('#input-dra', slots.dragons);
                    buildCoab(slots.coabilities, slots.adv.basename, slots.adv.wt);

                    const urlVars = getUrlVars();
                    if (urlVars.conf) { slots = loadConf(conf, slots); }

                    $('#wep-' + slots.adv.pref_wep).prop('selected', true);
                    $('#dra-' + slots.adv.pref_dra).prop('selected', true);
                    slots.adv.pref_wp.forEach((wp, i) => {
                        $(`#wp${i + 1}-` + wp).prop('selected', true);
                    });
                    for (const c of slots.adv.pref_coab) {
                        const check = $("input[id$='-" + c + "']");
                        check.prop('checked', true);
                        coabSelection(1, true);
                    }
                    selectSkillShare(slots.adv.basename, slots.adv.pref_share);
                    if (slots.adv.prelim) {
                        $('#test-warning').html('Warning: preliminary sim, need QC and optimization.');
                    } else {
                        $('#test-warning').empty();
                    }
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
                    if (slots.adv.afflict_res != undefined) {
                        for (const key in slots.adv.afflict_res) {
                            $('#input-res-' + key).val(slots.adv.afflict_res[key]);
                        }
                    } else {
                        for (const key in slots.adv.afflict_res) {
                            $('#input-res-' + key).removeAttr('value');
                        }
                    }
                    if (slots.adv.no_config != undefined) {
                        if (slots.adv.no_config.includes('wp')) {
                            $('.input-wp > div > select').prop('disabled', true);
                        }
                        if (slots.adv.no_config.includes('acl')) {
                            $('#input-edit-acl').prop('disabled', true);
                        }
                        if (slots.adv.no_config.includes('coab')) {
                            $('input.coab-check').prop('disabled', true);
                        }
                    } else {
                        $('.input-wp > div > select').prop('disabled', false);
                        $('#input-edit-acl').prop('disabled', false);
                        $('input.coab-check').prop('disabled', false);
                    }

                    if (slots.adv.equip === 'affliction') {
                        $('#input-sim-' + ELE_AFFLICT[slots.adv.ele]).val(100);
                    } else {
                        const simAff = $('#affliction-sim > div > input[type="text"]');
                        simAff.each(function (idx, res) { $(res).val(''); });
                    }

                    if (!set_equip) {
                        $('#input-equip').data('pref', slots.adv.equip);
                    }
                    if (slots.adv.tdps && slots.adv.equip != $('#input-equip').data('pref')) {
                        $('#input-teamdps').data('original', $('#input-teamdps').val());
                        $('#input-teamdps').val(slots.adv.tdps);
                    } else if ($('#input-teamdps').data('original')) {
                        $('#input-teamdps').val($('#input-teamdps').data('original'));
                        $('#input-teamdps').data('original', '');
                    }

                    $('#equip-' + (slots.adv.equip || 'base')).prop('selected', true);

                    runAdvTest(no_conf);
                }
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            $('#test-error').html('Failed to load adventurer');
        }
    });
}
function buildConditionList(conditions) {
    const conditionDiv = $('#input-conditions');
    conditionDiv.empty();
    for (cond in conditions) {
        if (cond.startsWith('hp')) {
            continue;
        }
        const newCondCheck = $('<div></div>').attr({ class: 'custom-control custom-checkbox custom-control-inline' });
        const newCondCheckInput = $('<input/>').attr({ id: 'input-cond-' + cond, type: 'checkbox', class: 'custom-control-input' }).prop('checked', conditions[cond]).data('cond', cond);
        const newCondCheckLabel = $('<label>' + cond + '</label>').attr({ for: 'input-cond-' + cond, class: 'custom-control-label' });
        newCondCheck.append(newCondCheckInput);
        newCondCheck.append(newCondCheckLabel);
        conditionDiv.append(newCondCheck);
    }
}
function readConditionList() {
    let conditions = {};
    const condCheckList = $('#input-conditions > div > input[type="checkbox"]');
    if (condCheckList.length === 0) {
        return null;
    } else {
        condCheckList.each(function (idx, condCheck) {
            conditions[$(condCheck).data('cond')] = $(condCheck).prop('checked');
        });
        return conditions;
    }
}
function readResistDict() {
    let resists = {};
    const resistList = $('#affliction-resist > div > input[type="text"]');
    if (resistList.length === 0) {
        return null;
    } else {
        resistList.each(function (idx, res) {
            const resVal = parseInt($(res).val());
            if (!isNaN(resVal) && resVal > 0) {
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
        const chain = kcoab[1];
        const ex = kcoab[2];
        check.data('name', k);
        check.data('chain', chain);
        check.data('ex', ex);
        check.change(checkCoabSelection);
        if (k == basename) {
            check.prop('disabled', true);
            check.prop('checked', true);
            found_basename = ex;
            $('#input-coabs').data('selfcoab', basename);
            // if (!chain || chain[2] != 'hp' + String.fromCharCode(8804) + '40') {
            //     check.prop('disabled', true);
            //     check.prop('checked', true);
            //     found_basename = ex;
            // } else {
            //     $('#input-coabs').data('self', basename);
            //     check.addClass('coab-check');
            // }
        } else {
            check.addClass('coab-check');
        }
        const label = $(`<label>${fullname}</label>`).addClass('custom-control-label').prop('for', cid);
        wrap.append(check);
        wrap.append(label);
        if (chain) {
            wrap.prop('title', chain.join('|') + ' - ' + ex);
        } else {
            wrap.prop('title', ex);
        }
        if (WEAPON_TYPES.includes(ex)) {
            $('#input-coabs-'+ex).append(wrap);
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
        return null;
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
            simBuff[key] = buff_value;
        }
    }
    if ($.isEmptyObject(simBuff)) {
        return null;
    }
    return simBuff;
}
function toggleInput(state) {
    $('input').prop('disabled', state);
    $('select').prop('disabled', state);
    if (!state) {
        coabSelection(0);
    }
}
function runAdvTest(no_conf) {
    if ($('#input-adv').val() == '') {
        return false;
    }
    toggleInput(true);
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
                    buildConditionList(res.condition);
                    const result = res.test_output.split('\n');
                    const cond_true = result[1].split(',');
                    const name = cond_true[1];
                    const icon_urls = slots_icon_fmt(cond_true);
                    let copy_txt = '**' + name + ' ' + requestJson['t'] + 's** ';
                    let new_result_item = $('<div></div>').attr({ class: 'test-result-item' });
                    new_result_item.append($(
                        '<h4 class="test-result-slot-grid"><div>' +
                        icon_urls[0] + '</div><div>' + name + '</div><div>' + icon_urls.slice(1).join('') + '</div></h4>'));
                    copy_txt += create_dps_bar(new_result_item, cond_true, undefined);
                    const logs = ['dragon', 'summation', 'action', 'timeline'].map(key => {
                        if (res.logs[key] !== undefined && res.logs[key] !== "") {
                            return res.logs[key];
                        } else {
                            return false;
                        }
                    }).filter(l => (l));
                    $('#damage-log').html(logs.join('<hr class="log-divider">'));
                    $('#test-results').prepend(new_result_item);
                    $('#copy-results').prepend($('<textarea>' + copy_txt + '</textarea>').attr({ class: 'copy-txt', rows: (copy_txt.match(/\n/g) || [0]).length + 1 }));
                    update_teamdps();
                }
            }
            toggleInput(false);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            $('#test-error').html('Failed to run damage simulation');
            toggleInput(false);
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
    if (localStorage.getItem('teamdps')) {
        selectedAdv = localStorage.getItem('teamdps');
        $('#input-teamdps').val(localStorage.getItem('teamdps'));
    } else {
        $('#input-teamdps').val(BASE_TEAM_DPS);
        localStorage.setItem('teamdps', BASE_TEAM_DPS);
    }
    // $('#input-missile').val('');
    $('#input-hp').val('');
    const resistList = $('#affliction-resist > div > input[type="text"]');
    resistList.each(function (idx, res) { $(res).val(''); });
    const simAff = $('#affliction-sim > div > input[type="text"]');
    simAff.each(function (idx, res) { $(res).val(''); });
    $('input:checked.coab-check').prop('check', false);
    for (let key of SIMULATED_BUFFS) {
        $('#input-sim-buff-' + key).val('');
    }
    $('#input-conditions').empty();
    $('#input-dragonbattle').val('');
    $('#input-equip').val($('#input-equip').data('pref') || 'base');
}
function resetTest() {
    updateUrl();
    clearResults();
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
function update_teamdps() {
    const tdps = $('#input-teamdps').val();
    if (!$('#input-teamdps').data('original')) {
        localStorage.setItem('teamdps', tdps);
    }
    $('.test-result-item').each((_, ri) => {
        const team_p = $(ri).data('team') / 100;
        const team_v = tdps * team_p;
        const dps_num = $(ri).find('.dps-num')[0];
        const new_total = $(dps_num).data('total') + team_v;
        $(dps_num).html(Math.ceil(new_total));
        let others = 0;
        $(ri).find('.result-slice').each((_, rs) => {
            const portion = (team_v > 0) ? Math.ceil(1000 * ($(rs).data('dmg') / new_total)) / 10 : Math.floor(1000 * ($(rs).data('dmg') / new_total)) / 10;
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
function changeEquip(){
    updateUrl();
    loadAdvSlots(true, true);
}
window.onload = function () {
    $('#input-adv').change(debounce(resetTest, 100));
    $('#input-equip').change(debounce(changeEquip, 100));
    $('#run-test').click(debounce(runAdvTest, 100));
    if (!localStorage.getItem('displayMode')) {
        localStorage.setItem('displayMode', 'Markdown');
    }
    setDisplay(localStorage.getItem('displayMode'));
    $('#display-mode').click(toggleDisplay);
    $('#clear-results').click(clearResults);
    $('#reset-test').click(resetTest);
    $('#input-edit-acl').change(editAcl);
    $('#input-teamdps').change(update_teamdps);
    // $('#input-wep').change(weaponSelectChange);
    clearResults();
    loadAdvWPList();
    loadGithubCommits();
}
