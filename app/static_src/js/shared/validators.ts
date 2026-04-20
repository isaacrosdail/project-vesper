// For frontend validation

import { title } from '../shared/utils';
import { ValidatableElement } from '../types';

type ValidatorFn = (value: string) => string | null;

const debounceTimers = new Map<string, ReturnType<typeof setTimeout>>();

/**
 * Show or clear the inline validation error for a given form field.
 * If `errorMsg` is non-null, displays the error message and marks the field invalid.
 * If `errorMsg` is null, hides the error and clears invalid state.
 * @param field String ID for input field
 * @param errorMsg String of error message from validator. Null represents valid.
 * @remarks
 * Assumes the error container is a sibling `<small>` element.
 */
export function handleErrorMessages(field: string, errorMsg: string | null = null) {
    const fieldEl = document.querySelector<ValidatableElement>(`#${field}`);
    if (!fieldEl) {
        throw new Error(`handleErrorMessages: no field #${field}`)
    }
    const errorBox = fieldEl.parentElement?.querySelector('small');
    if (!errorBox) {
        throw new Error(`handleErrorMessages: no <small> sibling for #${field}`)
    }

    if (errorMsg) {
        errorBox.style.visibility = 'visible';
        errorBox.textContent = errorMsg;
        fieldEl.classList.add('invalid');
    } else {
        errorBox.style.visibility = 'hidden';
        errorBox.textContent = '';
        fieldEl.classList.remove('invalid');
    }
}

/**
 * Returns `true` if input element is either disabled OR optional and blank.
 * @param fieldEl Current input field element
 * @param value 
 * @returns 
 */
function shouldSkipValidation(fieldEl: ValidatableElement, value: string): boolean {
    const isDisabled = fieldEl?.disabled;
    const isOptionalAndBlank = !value.trim() && !fieldEl?.required;
    return isDisabled || isOptionalAndBlank;
}

/**
 * Triggers validation via Proxy obj on field input. Debounced by 300ms.
 * @param proxyObj Proxy that triggers validation when field values are set
 * @param e Input event from the field
 */
function validateFieldOnInput(proxyObj: Record<string, string>, e: Event) {
    const target = e.target as ValidatableElement;
    const field = target.name;

    // Clear errors & bail for now-empty fields
    if (target.value === '') {
        handleErrorMessages(field, null);
        clearTimeout(debounceTimers.get(field));
        return;
    }

    clearTimeout(debounceTimers.get(field));
    debounceTimers.set(field, setTimeout(() => {
        proxyObj[field] = target.value;
    }, 300));
}

/**
 * Validates all fields in validatorMap on form submission.
 * 
 * Stops event propagation if any validation errors exist.
 * 
 * @param form Form being submitted
 * @param validatorMap Map of field `name`s to validator functions
 * @param e Submit event (propagation stopped if errors present)
 */
function validateFormOnSubmit(form: HTMLFormElement, validatorMap: Record<string, ValidatorFn>, e: Event) {
    let hasErrors = false;

    // Check if valid, loop thru validatormap
    Object.entries(validatorMap).forEach(([field, validatorFn]) => {
        const fieldEl = form.querySelector<ValidatableElement>(`[name="${field}"]`);
        if (!fieldEl) {
            throw new Error(`validateFormOnSubmit: no field [name="${field}"] in form`)
        }
        const value = fieldEl.value;

        if (shouldSkipValidation(fieldEl, value)) {
            return;
        }
        const result = validatorFn(value)

        if (result !== null) {
            handleErrorMessages(field, result);
            hasErrors = true;
        }
    });

    // Prevent submission if errors
    if (hasErrors) {
        e.stopPropagation();
    }
}

/**
 * Initializes validation for a form by attaching input & submit listeners.
 * 
 * Sets up:
 * - Debounced validation (300ms) on each input field as user types
 * - Full validation on form submission (blocks submission if errors exist)
 * 
 * Input `name` attributes must match keys in `validatorMap`.
 * 
 * @param form Reference to the form element to validate
 * @param validatorMap Map of field `name`s to validator functions
 * @throws {Error} If the form reference is null or undefined.
 */
export function initValidation(form: HTMLFormElement, validatorMap: Record<string, ValidatorFn>) {
    if (!form) throw new Error('Error[initValidation]: invalid/missing form ref');

    const fieldEls = new Map<string, ValidatableElement>();

    Object.keys(validatorMap).forEach(field => {
        const el = form.querySelector<ValidatableElement>(`[name="${field}"]`);
        if (!el) throw new Error(`initValidation: no field [name="${field}"] in form`);
        fieldEls.set(field, el);
    
        // Debounced proxy trigger for input fields. Timers per field
        el.addEventListener('input', (e) => validateFieldOnInput(proxyObj, e));
    });

    // Proxy to validate on debounced input
    const proxyObj = new Proxy<Record<string, string>>({}, {
        set(target, property, value) {
            if (typeof property !== 'string' || !fieldEls.has(property)) {
                return true;
            }

            const field = fieldEls.get(property)!
            if (shouldSkipValidation(field, value)) {
                target[property] = value;
                return true;
            }

            target[property] = value;
            const validatorResult = validatorMap[property](value);
            handleErrorMessages(property, validatorResult);
            return true;
        }
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        validateFormOnSubmit(form, validatorMap, e);
    });
}

type StringRules = {
    maxLength?: number;
    minLength?: number;
    pattern?: RegExp;
    patternMsg?: string;
}
type NumericRules = {
    numType: 'int' | 'float';
    min?: number;
    max?: number;
}

type ValidationRule = StringRules | NumericRules;

/**
 * Factory function to create validator as per the given ruleset.
 */
export function makeValidator(fieldName: string, rules: ValidationRule): ValidatorFn {
    return (value: string): string | null => {
        const fieldDisplay = title(fieldName);

        if ('numType' in rules) {
            const num = rules.numType === 'int'
                ? parseInt(value, 10)
                : parseFloat(value);

            if (isNaN(num)) return `${fieldDisplay} must be a number`;
            if (rules.min !== undefined && num < rules.min)
                return `${fieldDisplay} must be at least ${rules.min}`;
            if (rules.max !== undefined && num > rules.max)
                return `${fieldDisplay} must be less than ${rules.max}`;
        } else {
            if (rules.maxLength && value.length > rules.maxLength)
                return `${fieldDisplay} must be under ${rules.maxLength} characters`;
            if (rules.minLength && value.length < rules.minLength)
                return `${fieldDisplay} must be at least ${rules.minLength} characters`;
            if (rules.pattern && !rules.pattern.test(value))
                return rules.patternMsg ?? `${fieldDisplay} invalid pattern.`;
        }
        return null;
    };
}
