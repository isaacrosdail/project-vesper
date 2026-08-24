// For frontend validation

import { title } from '../shared/formatters';
import type { ValidatableElement } from '../types';

type ValidatorFn = (value: string) => string | null;

// const debounceTimers = new Map<string, ReturnType<typeof setTimeout>>();
const DEBOUNCE_MS = 300;

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
 * Returns `true` if input element is either disabled OR optional and blank.
 */
function shouldSkipValidation(fieldEl: ValidatableElement, value: string): boolean {
    const isDisabled = fieldEl?.disabled;
    const isOptionalAndBlank = !value.trim() && !fieldEl?.required;
    return isDisabled || isOptionalAndBlank;
}

/**
 * Wires a form for inline validation. Per-field, debounced while typing.
 */

export function initValidation(form: HTMLFormElement, validatorMap: Record<string, ValidatorFn>) {
    if (!form) throw new Error('initValidation: missing form ref');

    const fieldEls = new Map<string, ValidatableElement>();
    const debounceTimers = new Map<string, ReturnType<typeof setTimeout>>();

    function showError(field: string, errorMsg: string | null) {
        const fieldEl = fieldEls.get(field)!;
        const errorBox = fieldEl.parentElement?.querySelector('small');
        if (!errorBox) throw new Error(`initValidation: no <small> sibling for [name="${field}"]`);

        errorBox.style.visibility = errorMsg ? 'visible' : 'hidden';
        errorBox.textContent = errorMsg ?? '';
        fieldEl.classList.toggle('invalid', errorMsg !== null);
    }

    function validateField(field: string, value: string): string | null {
        const fieldEl = fieldEls.get(field)!;
        if (shouldSkipValidation(fieldEl, value)) return null;
        return validatorMap[field](value);
    }

    for (const field of Object.keys(validatorMap)) {
        const el = form.querySelector<ValidatableElement>(`[name="${field}"]`);
        if (!el) throw new Error(`initValidation: no field [name="${field}"] in form`);
        fieldEls.set(field, el);

        el.addEventListener('input', () => {
            clearTimeout(debounceTimers.get(field));
            if (el.value === '') {
                showError(field, null);
                return;
            }
            debounceTimers.set(field, setTimeout(() => {
                showError(field, validateField(field, el.value));
            }, DEBOUNCE_MS));
        });
    }

    form.addEventListener('submit', (e) => {
        let hasErrors = false;
        for (const [field, el] of fieldEls) {
            clearTimeout(debounceTimers.get(field));
            const result = validateField(field, el.value);
            showError(field, result);
            if (result !== null) hasErrors = true;
        }
        if (hasErrors) e.preventDefault();
    });
}


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
