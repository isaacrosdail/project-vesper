
import { api } from '../services/api';
import { userStore } from '../services/userStore';
import { calculateBMR, readField, restoreOriginal, swapField, swapToInput, swapToText } from '../utils';
import { makeToast } from './toast';


function setEditMode(section: HTMLElement, editing: boolean) {
    section.querySelector(`.edit-btn`).classList.toggle('hide', editing);
    section.querySelector(`.save-btn`).classList.toggle('hide', !editing);
    section.querySelector(`.cancel-btn`).classList.toggle('hide', !editing);
}

let defaultTargets = {};

const CAL_PER_GRAM = { fat_target: 9, protein_target: 4, carbs_target: 4 };

export function pctToGrams(calories: number, pct: number, macro: 'fat_target' | 'carbs_target' | 'protein_target'): number {
    return Math.round((Number(calories) * Number(pct) / 100) / CAL_PER_GRAM[macro]);
}
export function gramsToPct(calories: number, grams: number, macro: 'fat_target' | 'carbs_target' | 'protein_target'): number {
    return Math.round((Number(grams) * CAL_PER_GRAM[macro]) / Number(calories) * 100);
}
const USER_FIELDS = ['timezone', 'units', 'city', 'country'] as const;
const MACRO_FIELDS = ['fat_target', 'carbs_target', 'protein_target'] as const;


function loadDefaults() {
    // TODO: Note: timezone, units, city, country -> All actual user model fields
    // All else -> stored as key-vals in prefs
    const prefs = userStore.data.preferences || {};
    const { timezone, units, city, country } = userStore.data;

    // const weight = await apiRequest('GET', '/daily_metrics/')

    // selected = prefs.default_table || 'products';
    // defaultUnits = prefs.default_units || 'metric';
    // defaultTimeframe = Number(prefs.default_timeframe) || 30;
    defaultTargets = {
        weight_target: prefs.weight_target || '120',
        calories_target: prefs.calories_target || '2200',
        protein_target: prefs.protein_target || '150',
        fat_target: prefs.fat_target || '70',
        carbs_target: prefs.carbs_target || '250',
        birth_year: prefs.birth_year || 1900,
        weight_actual: prefs.weight_actual || 150, // TODO: This is an actual metric, should be pulled, not enterd here
        height_cm: prefs.height_cm || 999,
        sex: prefs.sex || 'm',
        timezone: timezone,
        units: units,
        city: city,
        country: country,
        time_format: prefs.time_format
    };
    // Adjust weight_target? read kg from db -> if imperial, convert to lbs and show
    // Save: if imperial, convert lbs to kg -> send kg to db

    // sync ui
    const targetVals = document.querySelectorAll('.target-value');
    targetVals.forEach(span => {
        const key = span.dataset.target;
        let stored = defaultTargets[key];
        // Convert grams -> % for display
        if (MACRO_FIELDS.includes(key)) {
            stored = gramsToPct(defaultTargets.calories_target, stored, key)
        }
        span.textContent = stored;
    })

}


export function init() {
    const sidebar = document.querySelector('.profile-sidebar');
    const backdrop = document.querySelector('.profile-sidebar-backdrop');
    if (!sidebar || !backdrop) { console.warn ('initProfileSidebar: sidebar/backdrop missing!') };

    loadDefaults();

    const bmr = calculateBMR(
        defaultTargets.sex,
        Number(defaultTargets.weight_actual),
        Number(defaultTargets.height_cm),
        Number(defaultTargets.birth_year)
    );
    document.querySelector('.bmr-display').textContent = `${Math.round(bmr)} kcal`;

    // Open/close
    const profileBtn = document.querySelector('.js-profile-btn');
    profileBtn?.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        backdrop.classList.toggle('open');
    });
    backdrop.addEventListener('click', () => {
        sidebar.classList.remove('open');
        backdrop.classList.remove('open');
    });

    // Edit/save/cancel per section
    sidebar.querySelectorAll('.sidebar-section').forEach(section => {
        const editBtn = section.querySelector('.edit-btn');
        const saveBtn = section.querySelector('.save-btn');
        const cancelBtn = section.querySelector('.cancel-btn');
        if (!editBtn || !saveBtn || !cancelBtn) return;

        editBtn.addEventListener('click', () => {
            setEditMode(section, true);
            // section.querySelectorAll('.target-value').forEach(span => swapToInput(span as HTMLElement));
            section.querySelectorAll('.target-value').forEach(swapField);
        });

        saveBtn.addEventListener('click', () => {
            const prefUpdates: Record<string, string> = {};
            const userUpdates: Record<string, string> = {};
            const pending: Record<string, string> = {};
            section.querySelectorAll('.target-value').forEach(span => {
                const key = (span as HTMLElement).dataset.target;
                const value = readField(span);
                if (key) pending[key] = value;
            });
            // Pass 2: validate macros sum, divvy into userUpdates vs prefUpdates
            const hasMacros = Object.keys(pending).some(x => MACRO_FIELDS.includes(x));
            if (hasMacros) {
                const macroSum = MACRO_FIELDS.reduce((sum, m) => sum + Number(pending[`${m}`] || 0), 0);
                if (macroSum !== 100) {
                    makeToast('Macro percentages must sum to 100', 'error');
                    return;
                }
            }
            Object.entries(pending).forEach(([key, val]) => {
                // validate macros sum to 100 and divvy into buckets for updates things
                if (USER_FIELDS.includes(key)) {
                    userUpdates[key] = val;
                // Need to store macros as grams, not percentages
                } else if (MACRO_FIELDS.includes(key)) {
                    const cals = Number(pending["calories_target"]);
                    prefUpdates[key] = String(pctToGrams(cals, Number(val), key))
                } else {
                    prefUpdates[key] = val;
                }
            })
            if (Object.keys(prefUpdates).length) {
                api.preferences.patch(prefUpdates)
            }
            if (Object.keys(userUpdates).length) {
                api.profile.patch(userUpdates)
            }
            setEditMode(section, false);
            section.querySelectorAll('.target-value').forEach(span => {
                const key = span.dataset.target;
                if (key) swapToText(span, pending[key])
            })
        });

        cancelBtn.addEventListener('click', () => {
            section.querySelectorAll('.target-value').forEach(restoreOriginal);
            setEditMode(section, false)
        });
    });
}