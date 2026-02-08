// Drafting some better frontend logging

class Logger {
    constructor(LOG_LEVEL) {
        this.LOG_LEVEL = 'DEBUG';
    }

    log(msg, data) {
        const err = new Error();
        // the stack trace from err.stack here shows the call chain, from
        // most recent -> oldest
        const thing = err.stack;
        // const split = err.stack.split('\n')[2].split(' ')
        // const split = err.stack.split('\n')
        // const func = split[5]
        // console.log(`func: ${func}`)
        // const thing2 = thing.replace(/s/g, 'g')
        // console.log(thing2);
        console.log(thing);
        console.log(`msg: ${msg}, data: ${data}`);
    }
}

// Singleton
export const logger = new Logger();

// test func
function greetMe() {
    const greeting = "hey you";
    logger.log(greeting)
}

greetMe();