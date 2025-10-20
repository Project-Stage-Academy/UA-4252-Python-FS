import '@testing-library/jest-dom';

window.URL.createObjectURL = jest.fn(() => "mock-url-for-test");