import {
  describe, it, beforeAll, beforeEach, afterEach, afterAll, expect, jest,
} from "@jest/globals";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom";
import PasswordResetConfirm from "./PasswordResetConfirm";

type FetchT = typeof global.fetch;
let originalFetch: FetchT;
let errorSpy: jest.SpyInstance;
let warnSpy: jest.SpyInstance;

const setUrlToken = (token?: string) => {
  const url = token ? `/reset-password?token=${token}` : "/reset-password";
  window.history.replaceState({}, "", url);
};

const mockFetchOnce = (status = 200, body?: any) => {
  (global.fetch as jest.Mock).mockResolvedValueOnce({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body ?? null,
  } as any);
};

const typeAndSubmit = async (pwd: string, confirm: string) => {
  const user = userEvent.setup();
  await user.type(screen.getByPlaceholderText(/новий пароль/i), pwd);
  await user.type(screen.getByPlaceholderText(/підтвердження/i), confirm);
  await user.click(screen.getByRole("button"));
};

describe("PasswordResetConfirm (UA)", () => {
  beforeAll(() => {
    originalFetch = global.fetch;
    errorSpy = jest.spyOn(console, "error").mockImplementation(() => {});
    warnSpy = jest.spyOn(console, "warn").mockImplementation(() => {});
  });

  beforeEach(() => {
    global.fetch = jest.fn() as any;
    setUrlToken("test-token"); // дефолт: є токен
  });

  afterEach(() => {
    global.fetch = originalFetch;
    jest.resetAllMocks();
  });

  afterAll(() => {
    errorSpy.mockRestore();
    warnSpy.mockRestore();
  });

  it("одразу показує invalid-UI, якщо токена немає", async () => {
    setUrlToken(undefined);
    render(<PasswordResetConfirm lang="uk" />);

    expect(
      await screen.findByText(/токен недійсний|строк його дії минув/i)
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /надіслати запит повторно/i })
    ).toBeInTheDocument();
  });

  it("показує повідомлення про слабкий пароль", async () => {
    render(<PasswordResetConfirm lang="uk" />);
    await typeAndSubmit("123", "123");

    expect(
      await screen.findByText(/не відповідає вимогам/i)
    ).toBeInTheDocument();
  });

  it("показує помилку, якщо паролі не співпадають", async () => {
    render(<PasswordResetConfirm lang="uk" />);
    await typeAndSubmit("StrongPass1!", "OtherPass1!");

    expect(
      await screen.findByText(/паролі не співпадають/i)
    ).toBeInTheDocument();
  });

  it("рендерить success-UI при 200 OK", async () => {
    mockFetchOnce(200);
    render(<PasswordResetConfirm lang="uk" />);

    await typeAndSubmit("StrongPass1!", "StrongPass1!");

    expect(
      await screen.findByText(/пароль успішно змінено/i)
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /увійти/i })).toBeInTheDocument();
  });

  it("рендерить invalid-UI при 400 (недійсний токен)", async () => {
    mockFetchOnce(400);
    render(<PasswordResetConfirm lang="uk" />);

    await typeAndSubmit("StrongPass1!", "StrongPass1!");

    expect(
      await screen.findByText(/токен недійсний|строк його дії минув/i)
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /надіслати запит повторно/i })
    ).toBeInTheDocument();
  });
});
