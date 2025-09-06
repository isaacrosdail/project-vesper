
// between(): From a given string, return the substring that is between two markers (left and right)
// EX: between("theme=dark;", "=", ";") would return "dark"

export function between(string: string, left: string, right: string): string {
    const l = string.indexOf(left) + left.length;
    if (l === -1) return "";
    console.log(l)
    let r = string.indexOf(right);
    if (r === -1) r = string.length;
    console.log(r)
    return string.slice(l, r);
}

// stripPrefix(): Remove a prefix if it exists, otherwise return original
// EX: stripPrefix("myVariable", "my") → "Variable"
// EX: stripPrefix("username", "my") → "username" (no change)
function stripPrefix(string: string, pref: string): string {
    if (!string.startsWith(pref)) return string;

    return string.slice(pref.length);
}

function stripSuffix(string: string, suff: string): string {
    if (!string.endsWith(suff)) return string;

    return string.slice(0, -suff.length);
}

// padBetween(): Add padding between two parts of a string
// EX: padBetween("Name", "Value", 20) → "Name            Value" (total 20 chars)
// EX: padBetween("ID", "12345", 10, "-") → "ID----12345" (using custom pad char)
function padBetween(start: string, end: string, pad: number, sym?: string): string {
    const contentLength = start.length + end.length;

    if (contentLength >= pad) {
        throw new Error(`Cannot fit ${contentLength} characters into ${pad} total characters.`);
    }

    const between = pad - contentLength;
    const symbol = sym || " ";
    return `${start}${symbol.repeat(between)}${end}`;
}

// so ...("hellooo", "o") results in "hello"
function removeConsecutive(string: string, char: string): string {
    let result = "";
    for (let i = 0; i < string.length; i++) {
        if (string[i] === char && string[i+1] === char) {
            continue
        }
        result += string[i];
    }
    return result;
}

function capitalizeAfter(string: string, cap: string): string {
    let result = "";
    let capNext = false;
    for (let i = 0; i < string.length; i++) {
        if (cap.includes(string[i])) {
            capNext = true; // set flag to capitalize NEXT letter
            result += string[i];
        }
        else if (capNext) {
            result += string[i].toUpperCase();
            capNext = false;
        } else {
            result += string[i];
        }
        console.log(`${string[i]} -> ${result} || capNext: ${capNext}`)
    }
    return result;
}

// countNested("((hello)world(test))", "(", ")") → 2 (max depth)
// Track how deep the nesting goes
function countNested(string: string, open: string, close: string): number {
    let count = 0;
    let maxDepth = 0;
    for (let i = 0; i < string.length; i++) {
        if (string[i] === open) {
            count++;
        } else if (string[i] === close) {
            count--;
        }
        maxDepth = count > maxDepth ? count : maxDepth;
    }
    return maxDepth;
}

// extractQuoted('name="John Doe" age="25"', '"') → ["John Doe", "25"]
function extractQuoted(string: string, delimiter: string): string[] {
    let stretch = '';
    let results: string[] = [];
    let between = false;
    let seen = 0;
    for (let i = 0; i < string.length; i++) {
        if (string[i] === delimiter) {
            between = !between;
            seen++;
        }
        else if (between) {
            stretch += string[i];
            if (string[i+1] === delimiter) {
                results.push(stretch);
                stretch = '';
                seen = 0;
            }
        }
        console.log(`i=${i} || stretch: ${stretch}`)
    }
    return results;
}

// // const myStr = "hellooo"
// const myStr2 = "hello.world!how are.you"
// const myStr3 = "((hello)world(test))"
// const myStr4 = 'name="John Doe" age="25"'
// // console.log(removeConsecutive(myStr, "o"));
// // console.log(capitalizeAfter(myStr2, ".!"));
// // console.log(countNested(myStr3, "(", ")"));
// // console.log(extractQuoted(myStr4, '"'))

// // Normal case
// console.log(between("Hello [World]!", "[", "]"));
// // expected: "World"

// // Multiple candidates
// console.log(between("foo<bar>baz<qux>", "<", ">"));
// // expected: "bar" (stops at first ">")

// // No right delimiter
// console.log(between("abc [def", "[", "]"));
// // expected: "" (r = -1, slice(l, -1) → everything until last char)

// // No left delimiter
// console.log(between("abcdef]", "[", "]"));
// // expected: "abcdef" (l = -1 + 1 + length → weird index)

// // Overlapping markers
// console.log(between("start--middle--end", "--", "--"));
// // expected: "middle"