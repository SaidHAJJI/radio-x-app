module.exports = {
  testEnvironment: 'jest-environment-jsdom',
  setupFilesAfterEnv: ['@testing-library/jest-dom'],
  transform: {
    '^.+\\.jsx?$': 'babel-jest', // Transform JS/JSX files using Babel
  },
  moduleNameMapper: {
     // Handle CSS imports (if any in components)
     '\\.css$': 'identity-obj-proxy',
     // Handle static assets
     '\\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js',
  }
};
