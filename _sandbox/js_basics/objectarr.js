// Drilling syntax/structure/terminology of objects/arrays

// The value of books here is an array literal
// Each element inside that array is an object literal with:
//    title and author as property keys, and corresponding string literal values like 'Harry Potter'
const LIBRARY = {
    books: [
        {title: 'Harry Potter', author: 'George RR Martin'},
        {title: 'Game of Stones', author: 'Dr. Seuss'}
    ]
}

// 5. Write an object literal named APP_CONFIG with:
// A property theme whose value is an object containing:
// mode: 'dark'
// primaryColor: 'blue'
// A property features whose value is an array containing two strings: 'search' and 'notifications'.

const APP_CONFIG = {
    theme: {mode: 'dark', primaryColor: 'blue'},
    features: ['search', 'notifications']
}


// Taking our real MENU_CONFIG object example now
const MENU_CONFIG = {
    default: [
        {text: 'Edit', action: 'edit'},
        {text: 'Delete', action: 'delete'}
    ],
    products: [{text: 'Add to shopping list', action: 'addToShoppingList'}],
    transactions: [{text: 'Add to shopping list', action: 'addToShoppingList'}]
}

// Splicing together using spread operator
const subtype = 'products'; // using products as example
const items = [
    ...MENU_CONFIG.default, // this spreads the objects OUT of the array
    ...(MENU_CONFIG[subtype] || [])
]

console.log(items)

// So items becomes a flat array like:
// [
//     {text: 'Edit', action: 'edit'},
//     {text: 'Delete', action: 'delete'},
//     {text: 'Add to shopping list', action: 'addToShoppingList'}
// ]

// So now to access values:
// From MENU_CONFIG before spreading:
MENU_CONFIG.default[0].text   // -> 'Edit'
MENU_CONFIG.default[1].action // -> 'edit'

// From items after spreading
items[0].text
items[1].action


// Map/lookup pattern
const action = 'edit'; // original: e.target.dataset.action;

// This is just an object where keys are strings (duh), and values are function references (not calling them, just storing them)
const actionHandlers = {
    'edit': handleEdit,
    'delete': handleDelete,
    'addToShoppingList': handleAddToShoppingList
}

actionHandlers[action] // looks up 'delete' key -> gets handleDelete function
// This is the same as:
actionHandlers['delete']  // → handleDelete
actionHandlers.delete     // → handleDelete (dot notation works too)
// Calling the retrieved function:
actionHandlers[action]()  // Looks up the function AND calls it with ()
// So we can pass a parameter like:
actionHandlers[action](menu.context)  // Calls function with menu.context as argument

