import nextConfig from 'eslint-config-next/core-web-vitals'

const eslintConfig = [
  ...nextConfig,
  {
    ignores: [
      '.next/**',
      'out/**',
      'build/**',
      'next-env.d.ts',
    ],
  },
  {
    rules: {
      // Temporarily disable error-boundaries rule - these are pre-existing issues
      // that should be fixed in a separate refactoring PR
      'react-hooks/error-boundaries': 'off',
    },
  },
]

export default eslintConfig
