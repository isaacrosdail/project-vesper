// Utility (pure functions), import explicitly so they're tree-shaken otherwise?

/**
 * Bubble sort - Return sorted copy of input list.
 * - Stable
 * - Time: O(n^2) in worst/avg, O(n) best (already sorted)
 * - Space: O(n) due to shallow copy
 * @param list Array of items to sort.
 * @returns A new sorted array.
 */
export function _bubbleSortSimple<T>(list: T[]): T[] {
    const myList = [...list];

    for (let i = 0; i < myList.length - 1; i++) {
        // Outer loop decides whether to continue
        let didSwap = false;
        for (let j = 0; j < myList.length-i-1; j++) {
            // If arr[i] > arr[i+1], swap
            if (myList[j]! > myList[j+1]!) {
                [myList[j], myList[j + 1]] = [myList[j + 1]!, myList[j]!];
                didSwap = true;
            }
        }
        if (!didSwap) {
            break;
        }
    }
    return myList; // return sorted list
}

/**
 * Bubble sort - Return sorted copy of input list.
 * - Stable
 * - Time: O(n^2) worst/avg, O(n) best
 * - Space: O(n) due to shallow copy
 * @param list Array of objects to sort
 * @param key Key in the object to compare by
 * @param reverse If true, sort in ascending order
 * @returns A new sorted array (non-mutating)
 */
export function _bubbleSort<T, K extends keyof T>(
    list: T[],
    key: K,
    reverse = false
): T[] {
    const myList = [...list];

    for (let i = 0; i < myList.length -1; i++) {
        // Outer loop decides whether to continue
        let didSwap = false;
        for (let j = 0; j < myList.length -i-1; j++) {
            const a = myList[j]![key];
            const b = myList[j+1]![key];
            // Smaller bubbles up to end vs larger bubbles up
            const shouldSwap = reverse ? a < b : a > b;

            if (shouldSwap) {
                [myList[j], myList[j + 1]] = [myList[j + 1]!, myList[j]!];
                didSwap = false;
            }
        }
        // If we traverse the array once without swapping -> list is sorted
        if (!didSwap) {
            break;
        }
    }
    return myList; // Return sorted list
}

// debug
const numbers = [
    {
        'name': 'Steve',
        'age': 20
    },
    {
        'name': 'John',
        'age': 23
    },
    {
        'name': 'Raliegh',
        'age': 25
    },
    {
        'name': 'Stan',
        'age': 26
    }
];
const sortedNumbers = _bubbleSort(numbers, 'name');
console.log("Sorted:")
console.log(sortedNumbers);  // [1, 2, 5, 8, 9]
console.log("Original:")
console.log(numbers);        // [5, 2, 8, 1, 9] - original unchanged!