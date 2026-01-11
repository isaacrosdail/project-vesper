
/* Function* with yield statements
Auto-implements iterator protocol
Lazy evaluation by default
Can accept values via next(val) and yield expressions
*/

function* range(start, end) {
  for (let i = start; i < end; i++) {
    yield i;
  }
}