import css from "@eslint/css";
import js from "@eslint/js";
import { defineConfig } from "eslint/config";
import globals from "globals";
import svelte from 'eslint-plugin-svelte';
import prettier from 'eslint-config-prettier';
import tseslint from "typescript-eslint";

export default defineConfig([
  {
    files: ["**/*.{js,mjs,cjs,ts,mts,cts}"],
    plugins: { js },
    extends: ["js/recommended"],
    languageOptions: { globals: globals.browser },
  },
  tseslint.configs.recommended,

  {
    files: ["**/*.svelte", "**/*.svelte.{js,ts}"],
    extends: [svelte.configs.recommended],
    languageOptions: { parserOptions: { parser: tseslint.parser } },
  },
  {
    files: ["**/*.css"],
    plugins: { css },
    language: "css/css",
    extends: ["css/recommended"],
    rules: {
        "css/use-baseline": ["warn", { available: "newly" }],
        "css/no-invalid-properties": ["error", { allowUnknownVariables: true }],
    },
  },

  prettier,
  {
    files: ["**/*.svelte", "**/*.svelte.{js,ts}"],
    extends: [svelte.configs.prettier],
  }
]);
