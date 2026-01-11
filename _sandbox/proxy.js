
const proxyObj = new Proxy({}, {
    get(target, property) {
        console.log(`Someone asked for: ${property}`);
        return target[property];
    },

    set(target, property, value) {
        console.log(`Someone set ${property} to ${value}`);
        target[property] = value;
        return true; // Must return true for set to work (good move, JS peeps, well played here)
    }
});

proxyObj.name = "Bob";
proxyObj.age = 25;
console.log(proxyObj.name);