import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import { defineConfig } from "eslint/config";


export default defineConfig([
  // Adding ignores
  {
    ignores: [
      ".venv/**",
      "**/site-packages/**",
      "**/werkzeug/**",
      "**/coverage/**",
      "htmlcov/**",
      "node_modules/**", // redundant?

      // Config files
      "*.config.js", // Ignore Jest, Tailwind config files
      "*.config.ts"
    ]
  },
  { files: ["**/*.{js,mjs,cjs,ts,mts,cts}"], plugins: { js }, extends: ["js/recommended"] },

  { 
    files: ["**/*.{js,mjs,cjs,ts,mts,cts}"],
    languageOptions: { globals: { ...globals.browser, ...globals.node } },
  
    // Adding rules to make ESLint respect the _ prefix
    rules: {
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          "varsIgnorePattern": "^_", // Ignores unused variables & functions (like our bubbleSort for now)
          "argsIgnorePattern": "^_"  // Ignores unused function parameters
        }
      ]
    }
  },
  tseslint.configs.recommended,

  // Special config for test files
  {
    files: ["**/*.test.{js,ts}", "tests/**/*.{js,ts}"],
    languageOptions: {
      globals: {
        ...globals.jest,  // Adds test, expect, describe, etc.
        ...globals.node   // Add Node.js globals (includes require, module, etc.)
      }
    }
  }
]);
