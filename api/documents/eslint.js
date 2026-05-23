module.exports = {
    env: {
        "browser": true,
        "es2021": true
    },
    extends: [
        "eslint:recommended",
        "plugin:@typescript-eslint/recommended",
        "plugin:react/recommended",
    ],
    overrides: [
        {
            env: {
                node: true
            },
            files: [
                '.eslintrc.{js,cjs}',
                'src'
            ],
            parserOptions: {
                sourceType: 'script'
            }
        }
    ],
    parser: "@typescript-eslint/parser",
    parserOptions: {
        "ecmaVersion": "latest",
        "sourceType": "module",
        "parser": '@typescript-eslint/parser',
        "project": 'tsconfig.eslint.json'
    },
    plugins: [
        "@typescript-eslint",
        "react",
        'unused-imports'
    ],
    rules: {
        '@typescript-eslint/consistent-type-assertions': 'off',
        '@typescript-eslint/strict-boolean-expressions': 'off',
        'no-async-promise-executor': 'warn',
        'unused-imports/no-unused-imports': 'error',
    }
} 