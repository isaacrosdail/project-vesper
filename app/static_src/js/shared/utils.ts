// Misc. utilities

// TODO: Make this minIncl, maxExcl & ensure callsites are updated
// half-open intervals follows indexing/iteration
// this way the end is the length or count, not the last valid index
export const randInt = (min: number, max: number) =>
    // remove +1 here
    Math.floor(Math.random() * (max - min + 1)) + min;

export const randFloat = (min: number, max: number) =>
    (Math.random() * (max - min) + min);


export const debounce = (callback: Function, wait: number) => {
    let timeoutId: number;
    return (...args: unknown[]) => {
        window.clearTimeout(timeoutId);
        timeoutId = window.setTimeout(() => {
            callback(...args);
        }, wait);
    }
}

const KG_TO_LBS = 2.20462;
export const lbsToKg = (lbs: number) => lbs / KG_TO_LBS;
export const kgToLbs = (kg: number) => kg * KG_TO_LBS;

// Mifflin-St Jeor equation for resting BMR calculation.
export function calculateBMR(
    sex: 'f' | 'm',
    weightKG: number,
    heightCM: number,
    birthYear: number,
    currentYear: number = new Date().getFullYear()
): number {
    // Females: (10 * weight[kg]) + (6.25 * height[cm]) - (5 * age[yrs]) - 161
    // Males:   (10 * weight[kg]) + (6.25 * height[cm]) - (5 * age[yrs]) + 5
    const age = currentYear - birthYear
    const constant = sex === 'f' ? -161 : 5;
    return (10 * weightKG) + (6.25 * heightCM) - (5 * age) + constant;
}





export const divmod = (a: number, b: number): [quotient: number, remainder: number] => {
    if (b === 0) throw new Error(`Div by zero: a: ${a}, b: ${b}`);
    return [Math.floor(a/b), Math.abs(a % b)];
}
