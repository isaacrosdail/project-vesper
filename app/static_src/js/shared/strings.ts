
// between(): From a given string, return the substring that is between two markers (left and right)
// EX: between("theme=dark;", "=", ";") would return "dark"

export function between(string: string, left: string, right: string): string {
    const l = string.indexOf(left) + left.length;
    if (l === -1) return "";
    let r = string.indexOf(right);
    if (r === -1) r = string.length;
    return string.slice(l, r);
}
