import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import { defineConfig } from "eslint/config";


export default defineConfig([
  // === Ignores ===
  {
    ignores: [
      ".venv/**",
      "**/site-packages/**",
      "**/werkzeug/**",
      "**/coverage/**",
      "htmlcov/**",
      "node_modules/**",
      "*.config.js",
      "*.config.ts",
    ]
  },

  // === Base JS + TS ===
  js.configs.recommended,
  tseslint.configs.recommended,

  { 
    files: ["**/*.{js,mjs,cjs,ts,mts,cts}"],
    languageOptions: { globals: { ...globals.browser, ...globals.node } },
    rules: {  // Adding rules to make ESLint respect the _ prefix
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          "varsIgnorePattern": "^_", // Ignores unused variables & functions (like our bubbleSort for now)
          "argsIgnorePattern": "^_"  // Ignores unused function parameters
        }
      ],
      "eqeqeq": "error", // enforces strict equality (=== and !==) instead of looser equality operators (== and !==)
      "no-console": "off"
    }
  },

  // === Tests ===
  {
    files: ["**/*.test.{js,ts}", "tests/**/*.{js,ts}"],
    languageOptions: {
      globals: {
        ...globals.node   // Add Node.js globals (includes require, module, etc.)
      }
    }
  }
]);
