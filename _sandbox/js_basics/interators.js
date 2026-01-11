
// Object with next() method returning {value, done}
// Must track own state
// Often paired with Symbol.iterator method
// Manual control vs generator convenience trade-off

const range = {
  start: 0, end: 3, current: 0,
  [Symbol.iterator]() { return this; }, // what happens when it's NOT paired with Symbol.iterator?
  next() {
    return this.current < this.end 
      ? { value: this.current++, done: false }
      : { done: true };
  }
};