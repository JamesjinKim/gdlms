/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution');

module.exports = {
  root: true,
  extends: [
    'plugin:vue/vue3-essential',
    'eslint:recommended',
    '@vue/eslint-config-prettier',
  ],
  env: {
    'vue/setup-compiler-macros': true,
  },
  parserOptions: {
    // ecmaVersion: '2022',
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    'no-unused-vars': 'off',
    'no-console': 'off',
    // "no-console": process.env.NODE_ENV === "production" ? "error" : "off",
    // "no-debugger": process.env.NODE_ENV === "production" ? "error" : "off"
    'vue/html-self-closing': 'off', //<input></input>
    'vue/no-parsing-error': [
      2,
      {
        //<input></input>
        'x-invalid-end-tag': false,
      },
    ],
    'vue/multi-word-component-names': [
      'error',
      {
        ignores: ['Spinner', 'Dialog', 'Header', 'Navigation'],
      },
    ],
    'prettier/prettier': [
      'error',
      {
        singleQuote: true,
        semi: true,
        tabWidth: 2,
        trailingComma: 'all',
        printWidth: 80,
        bracketSpacing: true,
        arrowParens: 'avoid',
        endOfLine: 'auto', // 한줄 추가
      },
    ],
  },
};
