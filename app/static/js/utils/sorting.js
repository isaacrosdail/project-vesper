

// Stable
function bubbleSortSimple(myList){

    for (let i = 0; i < myList.length - 1; i++) {
        // Outer loop decides whether to continue
        let no_swaps = true;
        for (let j = 0; j < myList.length-i-1; j++) {
            // If arr[i] > arr[i+1], swap
            if (myList[j] > myList[j+1]) {
                no_swaps = false;
                let temp = myList[j];
                myList[j] = myList[j+1];
                myList[j+1] = temp;
            }
        }
        if (no_swaps) {
            break;
        }
    }
    return thing; // do we need to return here too?
}

function bubbleSort(myList, key, reverse=false) {

    for (let i = 0; i < myList.length -1; i++) {
        // Outer loop decides whether to continue
        let no_swaps = true;
        for (let j = 0; j < myList.length -i-1; j++) {
            // due to block scope, we need to declare this here:
            let should_swap;
            // Choose which comparison to use
            if (reverse) {
                // Swap current with next if it's less than (smaller bubbles up to end)
                should_swap = myList[j].key < myList[j+1].key;
            } else {
                // Swap current with next if it's greater than (larger bubbles up to end)
                should_swap = myList[j][key] > myList[j+1][key];
            }
            if (should_swap) {
                no_swaps = false;
                let temp = myList[j];
                myList[j] = myList[j+1];
                myList[j+1] = temp;
            }
        }
        // If we traverse the array once without swapping -> list is sorted
        if (no_swaps) {
            break;
        }
    }
}