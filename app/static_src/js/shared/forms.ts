

/**
 * Initialize "click eye icon for password/text toggle".
 * 
 * Conventions:
 * - Buttons must have a [data-password-toggle] attribute
 * - whose value = the ID of the <input type="password">
 * Script will:
 * - Find the target <input>
 * - Toggle type="password" <-> type="text" on click
 * - Reflect toggle state in `aria-pressed`
 * 
 * @example
 * <input id="pwd1" type="password">
 * <button data-password-toggle="pwd1">(eye)</button>
 */
export function initPasswordToggles() {
    const toggleButtons = document.querySelectorAll<HTMLElement>('[data-password-toggle]');
    if (toggleButtons.length === 0) return;

    toggleButtons.forEach(btn => {
        const inputId = btn.dataset["passwordToggle"];
        if (!inputId) return;
        const input = document.querySelector<HTMLInputElement>(`#${inputId}`);
        if (!input) return;
        const ariaPressed = input.type === 'text'
            ? 'true'
            : 'false';
        btn.setAttribute('aria-pressed', ariaPressed)

        btn.addEventListener('click', () => {
            const isPressed = btn.getAttribute('aria-pressed') === 'true';
            input.type = isPressed ? 'password' : 'text';
            btn.setAttribute('aria-pressed', String(!isPressed));
        })
    })
}

/**
 * TODO(forms): Integrate into Svelte stuff or purge.
 * Making my own type=number field.
 */
function setupNumericInputRestrictions() {
    const numberInputs = document.querySelectorAll('[data-type-int], [data-type-float]');
    // Don't impede functional keys
    const FUNCTIONAL_KEYS = [
        'Backspace', 
        'Delete',
        'Tab',
        'ArrowLeft', 
        'ArrowRight',
        'Home',         // Jump to start
        'End',          // Jump to end
    ];

    numberInputs.forEach(el => {
        const input = el as HTMLInputElement;
        const isFloat = input.hasAttribute('data-type-float');

        input.addEventListener('keydown', (e: KeyboardEvent) => {
            if (FUNCTIONAL_KEYS.includes(e.key)) {
                return;
            }

            // Arrows up/down to inc/dec
            if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                const currVal = input.value;
                let num = isFloat
                    ? parseFloat(currVal)
                    : parseInt(currVal, 10);
                
                if (isNaN(num)) {
                    num = 0;
                }

                const stepSize = parseFloat(input.dataset.step ?? '1'); // default 1 for ints
                const stepInterval = e.key === 'ArrowDown'
                    ? -stepSize
                    : stepSize;
                
                const newVal = Math.max(0, num + stepInterval);
                const multiplier = 1 / stepSize;
                const roundedVal = isFloat
                    ? Math.round(newVal * multiplier) / multiplier
                    : newVal;

                if (roundedVal === 0) {
                    input.value = '';
                } else {
                    input.value = String(roundedVal);
                }

                input.dispatchEvent(new Event('input', { bubbles: true }));
                e.preventDefault();
                return;
            }

            // Allow: Ctrl+A, Ctrl+C
            if (e.ctrlKey || e.metaKey) return;
            // Allow digits
            if (/^\d+$/.test(e.key)) return;
            // Allow '.' for floats
            if (isFloat && e.key === '.') return;

            e.preventDefault();
        });

        input.addEventListener('paste', (e) => {
            const pastedText = e.clipboardData?.getData('text') ?? '';

            // Validation RegEx
            const isValid = isFloat
                ? /^\d*\.?\d*$/.test(pastedText) // digits w/optional single '.'
                : /^\d+$/.test(pastedText)       // digits only

            if (!isValid) {
                e.preventDefault();
            }
        });
    })
}

// Shared by product and transaction forms
// const validateNetWeight = makeValidator('net_weight', {
//     numType: 'float', min: 0,
// });

// const validateCalories = makeValidator('calories_per_100g', {
//     numType: 'float', min: 0, max: 900,
// });

// const validateBarcode = makeValidator('barcode', {
//     minLength: 8, maxLength: 14, pattern: /^\d+$/
// });

// const validateProductName = makeValidator('name', {
//     maxLength: 80,
// });


initPasswordToggles();