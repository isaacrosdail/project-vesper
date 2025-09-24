// Currently for dynamically ommitting "nonsensical" units in add_product & add_transaction forms


function filterUnitOptions() {
    const categoryElement = document.querySelector('#category');
    const unitSelect = document.querySelector('#unit_type');
    if (!categoryElement || !unitSelect) return;

    const categorySelection = categoryElement.value;
    const unitTypes = unitSelect.querySelectorAll('option');
    
    // JS Object, use keys for types of groups, values are list of units allowed for that group
    const unitGroups = {
        weight: ['g', 'kg', 'oz', 'lb'],
        volume: ['ml', 'l', 'fl_oz']
    }
    // Map categories to groups: keys are categories, values are groups (in turn, keys for above dict)
    const unitOptionsMap = {
        drink: "volume",
        energy_drink: "volume",
        condiments_and_sauces: "volume",

        produce: "weight",
        dairy: "weight",
        grain: "weight",
        nut: "weight",
        meat: "weight",
    }

    // Use 2-step lookup with dict keys to store the appropriate list of allowed units for the given selection in allowedUnits
    const allowedUnits = unitGroups[unitOptionsMap[categorySelection]];

    // Then loop through each unit option and hide it if it's NOT n the allowed units list
    unitTypes.forEach(option => {
        option.hidden = !allowedUnits.includes(option.value);
    });
}

export function initProductForms() {
    if (!document.querySelector('.grocery-form')) return;

    document.addEventListener('change', (e) => {
        if (e.target.matches('#category')) {
            filterUnitOptions();
        }
    });
}

/**
 * Initialize "click eye icon for password/text toggle".
 * 
 * Conventions:
 * - Buttons must have a [data-password-toggle] attribute
 * - whose value = the ID of the <input type="password">
 * Script will:
 * - Find the target <input>
 * - Toggle type="password" <-> type="text" on click
 * - Reflect toggle state in `aria-pressed`
 * 
 * @example
 * <input id="pwd1" type="password">
 * <button data-password-toggle="pwd1">(eye)</button>
 */
export function initPasswordToggles() {
    const toggleButtons = document.querySelectorAll('[data-password-toggle]');
    if (toggleButtons.length === 0) return;

    toggleButtons.forEach(btn => {
        const inputId = btn.dataset.passwordToggle;
        const input = document.querySelector(`#${inputId}`);
        if (!input) return;
        btn.setAttribute('aria-pressed', input.type === 'text' ? 'true' : 'false')

        btn.addEventListener('click', () => {
            const isPressed = btn.getAttribute('aria-pressed') === 'true';
            input.type = isPressed ? 'password' : 'text';
            btn.setAttribute('aria-pressed', String(!isPressed));
        })
    })
}

initProductForms();
initPasswordToggles();