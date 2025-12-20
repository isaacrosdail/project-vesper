/** @type {import("stylelint").Config} */
export default {
    "extends":
    [
        "stylelint-config-standard",
        "stylelint-config-recess-order"
    ],
    "rules": {
        "rule-empty-line-before": null,
        "at-rule-empty-line-before": null,
        "selector-class-pattern": "^([a-z][a-z0-9]*)(-[a-z0-9]+)*(--[a-z0-9-]+)?$", /* Allow BEM modifiers */
        "property-no-vendor-prefix": null,
        "no-descending-specificity": null,
    }
};
