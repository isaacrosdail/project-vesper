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

initProductForms();