// .map() practice / learning

// const newArr = arr.map((element, index, array) => {
       // return something
// });
// element – current value
// index – (optional) current index
// array – (optional) the array being mapped

// Square each number
const nums1 = [1, 2, 3, 4]
const squares = nums1.map(n => n * n);
// console.log(squares); // [1, 4, 9, 16]

// Format Strings
const names8 = ["alice", "bob"]
const upper = names8.map(name => name.toUpperCase());
// console.log(upper)

// Double the numbers
const nums8 = [2, 4, 6]
const doubled = nums8.map(n => n * 2);
// console.log(doubled);

// Add Index to each item
const words8 = ["a", "b", "c"];
const newArr2 = words8.map((word, i) => word+i);
// console.log(newArr2);

// Clean up messy data
const users8 = [
    { first: "alice", last: "JOHNSON"},
    { first: "BOB", last: "smith"},
];
const cleanArr8 = users8.map(user => {
    const first = user.first.toLowerCase();
    const last = user.last.toLowerCase();
    const cap = str => str.charAt(0).toUpperCase() + str.slice(1);
    return `${cap(first)} ${cap(last)}`;
});
// console.log(cleanArr8);

// Uppercase the words
const words = ["cat", "dog", "bird"];
const upperWords = words.map(word => word.toUpperCase());
// console.log(upperWords);

// Length of each word
const words2 = ["apple", "hi", "banana"];
const wordsLength = words2.map(word => word.length);
// console.log(wordsLength);

// Object to string
const users = [
  { name: "Alice", age: 20 },
  { name: "Bob", age: 30 },
];
const usersToString = users.map(user => {
    return `${user.name} is ${user.age}`;
});
// console.log(usersToString);

// Names only
const users3 = [
  { name: "Alice", age: 20 },
  { name: "Bob", age: 30 },
  { name: "Carol", age: 25 },
];
const firstNames = users3.map(user => user.name);
// console.log(firstNames);

// Ages only
const users4 = [
  { name: "Alice", age: 20 },
  { name: "Bob", age: 30 },
];
const agesOnly = users4.map(user => user.age);
// console.log(agesOnly);

// Labels
const products = [
  { id: 1, label: "Shoes" },
  { id: 2, label: "Hat" },
];
// Map to: ["Product 1: Shoes", "Product 2: Hat"]
const labels = products.map(p => `Product ${p.id}: ${p.label}`);
// console.log(labels);

// Affordable & in stock
const products6 = [
  { id: 1, name: "Shoes",  price: 79.99, inStock: true  },
  { id: 2, name: "Hat",    price: 19.5,  inStock: true  },
  { id: 3, name: "Socks",  price: 5.0,   inStock: false },
  { id: 4, name: "Bag",    price: 49.0,  inStock: true  },
];
// Keep items that are inStock AND price < 50,
// then map to strings like: "Hat — $19.50"
const newArr = products6
    .filter(p => p.price < 50 && p.inStock)
    .map(p => `${p.name} - $${p.price}`);
console.log(newArr);

// Active Adults
const users6 = [
  { name: "Tom",   age: 17, isActive: true  },
  { name: "Lucy",  age: 22, isActive: false },
  { name: "Ben",   age: 21, isActive: true  },
  { name: "Maya",  age: 28, isActive: true  },
];
// Keep users with age >= 21 AND isActive,
// then map to just their names.
const newArr3 = users6
    .filter(user => user.age >= 21 && user.isActive)
    .map(user => user.name);

console.log(newArr3);

// Open Tasks -> Labels
const todos = [
  { id: 101, title: "setup CI",      done: true  },
  { id: 102, title: "write tests",   done: false },
  { id: 103, title: "refactor utils",done: false },
];
// Keep tasks where done === false,
// then map to "Task 102: write tests"
const newArr4 = todos
    .filter(todo => !todo.done)
    .map(todo => `Task ${todo.id}: ${todo.title}`);

console.log(newArr4);