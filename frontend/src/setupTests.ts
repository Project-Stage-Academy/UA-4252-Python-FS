import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';

// @ts-ignore
global.TextEncoder = TextEncoder;
// @ts-ignore
global.TextDecoder = TextDecoder;


window.URL.createObjectURL = jest.fn(() => "mock-url-for-test");
