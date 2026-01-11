
// What does our friend 'var' do here that causes issues?
for (var i = 0; i < 3; i++) {
    const log = () => {
        console.log(i);
    }
    setTimeout(log, 100);
}


/**
 * Tracing:
 * 
 * The for loop runs synchronously -> all three iterations happen immediately
 * Each sets a setTimeout callback
 * But by the time the callbacks actually execute, the loop is done.
 * 
 * With var i:
 * - There's only one variable i for the entire loop (function-scoped, or global if not in a function)
 * - All 3 closures reference that same i
 * - By the time they execute, i is 3
 * Result: 3, 3, 3
 * 
 * With let i:
 * - Each iteration creates a new i (block-scoped to that iteration)
 * - Each closure captures its own i from that iteration
 * Result: 0, 1, 2
 */