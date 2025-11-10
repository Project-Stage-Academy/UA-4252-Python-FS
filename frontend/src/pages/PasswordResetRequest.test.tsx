import { describe, it, beforeAll, beforeEach, afterEach, afterAll, expect, jest } from "@jest/globals";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom";
import PasswordResetRequest from "./PasswordResetRequest";

let originalFetch: typeof global.fetch;
let errorSpy: jest.SpyInstance;
let warnSpy: jest.SpyInstance;

function mockFetchOnce(status = 200, body?: any) {
  const payload = body ?? null;
  const ok = status >= 200 && status < 300;

  (global.fetch as jest.Mock).mockResolvedValueOnce({
    ok,
    status,
    json: async () => payload,
    text: async () => (payload !== null ? JSON.stringify(payload) : ""),
    headers: { get: () => "application/json" },
  } as any);
}

describe("PasswordResetRequest (UA)", () => {
  beforeAll(() => {
    originalFetch = global.fetch;
    errorSpy = jest.spyOn(console, "error").mockImplementation(() => {});
    warnSpy = jest.spyOn(console, "warn").mockImplementation(() => {});
  });

  beforeEach(() => {
    global.fetch = jest.fn() as any;
  });

  afterEach(() => {
    global.fetch = originalFetch;
    jest.resetAllMocks();
  });

  afterAll(() => {
    errorSpy.mockRestore();
    warnSpy.mockRestore();
  });

  it("показує помилку 'обов’язкове поле', якщо email порожній", async () => {
    const user = userEvent.setup();
    render(<PasswordResetRequest lang="uk" />);

    await user.click(screen.getByRole("button", { name: "Надіслати запит" }));

    expect(
      await screen.findByText("Поле електронної пошти є обов’язковим.")
    ).toBeInTheDocument();
  });

  it("показує помилку 'некоректний формат', якщо email неправильний", async () => {
    const user = userEvent.setup();
    render(<PasswordResetRequest lang="uk" />);

    await user.type(screen.getByLabelText("Електронна пошта"), "not-an-email");
    await user.click(screen.getByRole("button", { name: "Надіслати запит" }));

    expect(
      await screen.findByText("Введіть коректну адресу електронної пошти.")
    ).toBeInTheDocument();
  });

  it("рендерить success-UI при 200 OK і надсилає правильний payload", async () => {
    const user = userEvent.setup();
    mockFetchOnce(200);
    render(<PasswordResetRequest lang="uk" />);

    await user.type(screen.getByLabelText("Електронна пошта"), "test@example.com");
    await user.click(screen.getByRole("button", { name: "Надіслати запит" }));

    expect(
      await screen.findByText("Ми надіслали інструкції з відновлення пароля на вашу електронну пошту.")
    ).toBeInTheDocument();

    expect(global.fetch).toHaveBeenCalledWith(
      "/api/auth/password-reset/",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "test@example.com" }),
      })
    );
  });

  it("рендерить той самий success-UI при помилці сервера (наприклад, 500) — без розкриття існування акаунта", async () => {
    const user = userEvent.setup();
    mockFetchOnce(500);
    render(<PasswordResetRequest lang="uk" />);

    await user.type(screen.getByLabelText("Електронна пошта"), "test@example.com");
    await user.click(screen.getByRole("button", { name: "Надіслати запит" }));

    expect(
      await screen.findByText("Ми надіслали інструкції з відновлення пароля на вашу електронну пошту.")
    ).toBeInTheDocument();
  });
});
