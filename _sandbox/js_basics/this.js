
// ===== NUMERO UNO =====

// // 'this' binding here is dynamic - its value/existence depends on the caller
// function sayName() {
//     console.log("this is: " , this);
//     console.log("this.name is: ", this.name);
// }

// const person = {
//     name: "Alice",
//     greet: sayName
// };

// const anotherPerson = {
//     name: "Bob",
//     greet: sayName
// }

// // sayName();      // here, it fails, because there's no 'this' to even refer to for this.name
// person.greet(); // here, 'this' refers to what's left of the dot operator/accesor -> person
// anotherPerson.greet();

// ===== NUMERO DOS =====

// const person = {
//     name: "Alice",
//     greet: function() {
//         console.log(this.name);
//     }
// };

// person.greet();

// const greetFunc = person.greet; // Assigns the greet function itself from person to greetFunc. If we did person.greet(), that'd assign the RESULT (undefined since it's console.log)
// greetFunc(); // Problem is: We're invoking the greet function from person, which uses 'this', but now, we use no dot operator. Therefore, 'this' is undefined cause there's not object/thing being referred to!

/* Lesson here:
    Dot operator present (person.greet()) -> this = thing before the dot
    No dot operator (greetFunc()) -> this = undefined (strict mode) or global object
*/



// ===== NUMERO TRES =====
// Now, for how this ties into D3
const chart = {
    radius: 100,
    draw: function() {
        console.log("Chart radius: ", this.radius);

        const elements = [1,2,3];
        elements.forEach(function(d) {
            console.log("Inside forEach, radius: ", this.radius);
        });
    }
};

chart.draw(); // Here, 'this' = chart

/* But, inside of the draw method:
    // The forEach callback is called by forEach itself, NOT by us with a dot operator.
    // So inside function(d), 'this' is whatever forEach decided it should be (usually undefined/global)
    elements.forEach(function(d) {...})
*/

// So, bringing this back to our D3 issues, let's review the structure of our chart classes:
class Chart {
    updateChart() { // Layer 1: this = Chart instance
        const groups = selectAll(...).data(...).join(
            enter => {} // this = Chart instance

            update => { // Layer 2: this = Chart instance still
                update.select('path')
                    .attrTween("d", function(d) { // Layer 3: D3 'hijacks' 'this' here!
                        // Now, 'this' = DOM element, NOT Chart
                    });
            }
        );
    }
}

// So what's the fix? Well, we can just store the reference to the class property before that:
update => {
    const arc = this.arc;  // Capture Chart's arc before going deeper

    update.select('path')
        .attrTween("d", function(d) {
            // 'this' = DOM element (what D3 set, and needed for _current)
            // 'arc' = Chart's arc (still accessible, captured via closure)
        });
}
// 