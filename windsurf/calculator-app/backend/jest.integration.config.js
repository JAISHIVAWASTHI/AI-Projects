module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/__tests__/integration/**/*.test.ts'],
  testTimeout: 30000, // 30 seconds timeout for integration tests
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  globalSetup: '<rootDir>/test/setup.integration.ts',
  globalTeardown: '<rootDir>/test/teardown.integration.ts',
  setupFilesAfterEnv: ['<rootDir>/test/setup.integration.env.ts'],
  collectCoverage: false, // Integration tests don't need coverage
};
