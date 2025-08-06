// Currently for dynamically ommitting "nonsensical" units in add_product & add_transaction forms


// filter unit_type options
function filterUnitOptions() {
    // if value is drink or energy_drink
    const categorySelection = document.getElementById('category').value;
    const allOptions = document.querySelectorAll('#unit_type option'); // Grab all options in select menu => returns a NodeList

    // debugging
    //console.log(`Category selected: ${categorySelection}`);
    // List to make this more readable
    const fluidUnits = ['drink', 'energy_drink', 'condiments_and_sauces'];
    const solidUnits = ['produce', 'diary', 'grain', 'nut', 'meat'];

    // if fluids => show only ml, l, fl oz
    if (fluidUnits.includes(categorySelection)) {
        // Use NodeList's forEach method to loop through
        // forEach takes a callback function which gets called for each element (ie, each select option)
        allOptions.forEach(function(option) {
            // if g, kg, lb, or oz -> option.hidden = true
            const weightUnits = ['g', 'kg', 'oz', 'lb'];
            option.hidden = weightUnits.includes(option.value);
        });
    // if solids => show only g, kg, lb, oz
    } else if (solidUnits.includes(categorySelection)) {
        allOptions.forEach(function(option) {
            const fluidUnits = ['ml', 'l', 'fl_oz'];
            option.hidden = fluidUnits.includes(option.value);
        });
    // Simply unhide all
    } else {
        allOptions.forEach(function(option) {
            option.hidden = false;
        });
    }
}


// Event listener using delegation for category dropdown changes
document.addEventListener('change', (e) => {

    // If what triggered the change is our select element of id category
    if (e.target.matches('#category')) {
        filterUnitOptions();
    }
});

document.addEventListener('DOMContentLoaded', () => {
    filterUnitOptions();
});