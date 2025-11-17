declare namespace NodeJS {
  interface Global {
    TextEncoder: typeof TextEncoder;
    TextDecoder: typeof TextDecoder;
  }
}

interface Window {
  location: {
    assign: jest.Mock;
    href: string;
  };
}
