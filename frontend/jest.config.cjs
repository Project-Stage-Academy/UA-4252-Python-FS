module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jest-environment-jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapper: {
    '\\.(css|scss)$': 'identity-obj-proxy',
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/src/mocks/fileMock.js'
  },
  globals: {
    'ts-jest': {
      tsconfig: '<rootDir>/tsconfig.app.json',
      isolatedModules: true
    }
  },
  moduleNameMapper: {
    '\\.(css|scss)$': 'identity-obj-proxy'
  }
};
