
import { initValidation, makeValidator } from './shared/validators';

export function init() {
    const form = document.querySelector<HTMLFormElement>('#register-form')!;

    const validateUsername = makeValidator('username', {
        minLength: 3,
        maxLength: 30,
        pattern: /^[\p{L}0-9_]+$/u,
        patternMsg: "Username may only contain letters, numbers, & underscores"
    });

    const validatePassword = makeValidator('password', {
        minLength: 5,
        maxLength: 128
    });

    initValidation(
        form,
    {
        username: validateUsername,
        password: validatePassword,
    });
}