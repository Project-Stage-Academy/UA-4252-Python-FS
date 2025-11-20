import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';
import 'whatwg-fetch';

if (typeof (global as any).TextDecoder === 'undefined') {
  (global as any).TextDecoder = class TextDecoder {
    decode(input: any) {
      return input.toString();
    }
  };
}

if (typeof window !== 'undefined') {
  if (!window.location.assign) {
    window.location.assign = jest.fn();
  }
  if (!window.location.replace) {
    window.location.replace = jest.fn();
  }
  if (!window.location.reload) {
    window.location.reload = jest.fn();
  }
}

if (typeof globalThis.fetch === 'undefined') {
  globalThis.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      status: 200,
      json: async () => ({}),
    })
  ) as any;
}
