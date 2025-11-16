/// <reference types="node" />

declare namespace jest {
  interface Matchers<R> {
    toBeCalled(): R;
  }
}

declare var describe: jest.Describe;
declare var test: jest.It;
declare var expect: jest.Expect;
declare var beforeAll: jest.Lifecycle;
declare var afterEach: jest.Lifecycle;
declare var afterAll: jest.Lifecycle;
