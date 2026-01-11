
const myList = [
    { date: '2025-10-01', steps: 8200 },
    { date: '2025-10-02', steps: 6400 },
    { date: '2025-10-04', steps: 6600 },
    { date: '2025-10-03', steps: 6700 },
    { date: '2025-10-05', steps: 6900 },
]

// extract all step vals into an array
// calc average

// .map() to extract
const steps = myList.map(d => d.steps);
// .reduce() to sum, then divide by length
const avg = steps.reduce((a, b) => a + b, 0) / steps.length;

console.log(`Steps: ${steps}, Avg: ${avg}`)

// .filter() practice/learning

// Lets you iterate over an array and keep only the elements that satisfy a given condition
// const result = array.filter((item, index, array) => {
//     return /* condition */
// });

// Like .map(), it doesnt mutate the original array, it returns a new one
// Filter only cares if your callback returns true or false
//    true  => keep the item in the new array
//    false => drop it


// Filter even numbers
const nums2 = [1, 2, 3, 4, 5, 6]
const filtered = nums2.filter(n => n % 2 === 0);
// console.log(filtered);

// Filter by string length
const words = ["hi", "apple", "dog", "banana"];
const wordsfiltered = words.filter(word => word.length > 3);
// console.log(wordsfiltered);

// Filter users over age 21
const users = [
  { name: "Tom", age: 17 },
  { name: "Lucy", age: 22 },
  { name: "Ben", age: 21 },
];
const usersFiltered = users.filter(user => user.age > 21);
// console.log(usersFiltered);


// Combo filter+map
// Filter out even numbers, then map them to their squares
const nums = [1, 2, 3, 4, 5, 6];
const numsFiltered = nums.filter(num => num % 2 === 0);
const final = numsFiltered.map(num => num ** 2);
// console.log(final);

// Chaining the above drill into one thing!
const final2 = nums
    .filter(num => num % 2 === 0)
    .map(num => num ** 2);

console.log(final2);