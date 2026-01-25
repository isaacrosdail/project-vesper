// For frontend validation. (Name might be bad, idk)

import { title } from '../shared/strings';
import { ValidatableElement } from '../types';

type ValidatorFn = (value: string) => string | null;

const debounceTimers: Record<string, ReturnType<typeof setTimeout>> = {};


/**
 * Show or clear the inline validation error for a given form field.
 * If `errorMsg` is non-null, displays the error message and marks the field invalid.
 * If `errorMsg` is null, hides the error and clears invalid state.
 * @param field String ID for input field
 * @param errorMsg String of error message from validator. Null represents valid.
 * @remarks
 * Assumes the error container is a sibling `<small>` element.
 */
function handleErrorMessages(field: string, errorMsg: string | null = null) {
    const fieldEl = document.querySelector<ValidatableElement>(`#${field}`)!;
    const errorBox = fieldEl.parentElement?.querySelector('small')!;

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
function shouldSkipValidation(fieldEl: ValidatableElement | null, value: string): boolean {
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
        clearTimeout(debounceTimers[field]);
        return;
    }

    clearTimeout(debounceTimers[field]);
    debounceTimers[field] = setTimeout(() => {
        proxyObj[field] = target.value;
    }, 300);
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
        const fieldEl = form.querySelector(`[name="${field}"]`) as ValidatableElement;
        const value = fieldEl.value;
        const result = validatorFn(value)

        if (shouldSkipValidation(fieldEl, value)) {
            return;
        }
        if (result !== null) {
            handleErrorMessages(field, result);
            hasErrors = true;
        }
    });

    // Prevent submission in presence of errors
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
    if (!form) {
        throw new Error('Error: invalid/missing form ref')
    }

    const formEls = form.querySelectorAll<ValidatableElement>('input, textarea');

    // Proxy to validate on debounced input
    const proxyObj = new Proxy<Record<string, string>>({}, {
        set(target, property, value, _receiver) {
            if (!(typeof property === 'string' && validatorMap[property])) {
                return true;
            }

            const field = form.querySelector<ValidatableElement>(`[name="${property}"]`);

            if (shouldSkipValidation(field, value)) {
                target[property] = value;
                return true;
            }

            target[property] = value;
            const validatorResult = validatorMap[property](value);
            handleErrorMessages(property, validatorResult);

            // Cross-field validation for time_tracking
            // TODO: Formalize as this expands
            if (['started_at', 'ended_at'].includes(property)) {
                const [start, end] = [target['started_at'], target['ended_at']]
                if (!start || !end) return true;

                const message = start < end ? null : 'Times must be in order';
                handleErrorMessages('started_at', message);
                handleErrorMessages('ended_at', message);
            }

            return true;
        }
    });

    // Debounced proxy trigger for input fields. Timers per field
    formEls.forEach(el => {
        el.addEventListener('input', (e) => {
            validateFieldOnInput(proxyObj, e);
        });
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        validateFormOnSubmit(form, validatorMap, e);
    });
}

export type ValidationRule = {
    maxLength?: number;
    minLength?: number;
    isInt?: boolean;
    isFloat?: boolean;
    min?: number;
    max?: number;
    pattern?: RegExp;
    patternMsg?: string;
}

/**
 * Factory function to create validator as per the given ruleset.
 */
export function makeValidator(fieldName: string, rules: ValidationRule): ValidatorFn {
    return (value: string): string | null => {

        const fieldDisplay = title(fieldName);

        if (rules.maxLength && value.length > rules.maxLength) {
            return `${fieldDisplay} must be under ${rules.maxLength} characters`;
        }
        if (rules.minLength && value.length < rules.minLength) {
            return `${fieldDisplay} must be at least ${rules.minLength} characters`;
        }
        if (rules.isInt || rules.isFloat) {
            if (rules.isInt && rules.isFloat) {
                throw new Error('RealityError: Cannot have both isInt and isFloat')
            }
            const num = rules.isInt
                ? parseInt(value, 10)
                : parseFloat(value);

            if (isNaN(num)) return `${fieldDisplay} must be a number`;
            if (rules.min !== undefined && num < rules.min) {
                return `${fieldDisplay} must be at least ${rules.min}`
            }
            if (rules.max !== undefined && num > rules.max) {
                return `${fieldDisplay} must be less than ${rules.max}`
            }
        }
        if (rules.pattern && !rules.pattern.test(value)) {
            return rules.patternMsg
                ? rules.patternMsg
                : `${fieldDisplay} invalid pattern.`
        }
        return null;
    }
}
