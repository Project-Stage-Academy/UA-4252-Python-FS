import { describe, it, beforeAll, beforeEach, afterEach, expect, jest } from "@jest/globals";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom";
import PasswordResetRequest from "./PasswordResetRequest";

let originalFetch: typeof global.fetch;

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
  });

  beforeEach(() => {
    global.fetch = jest.fn() as any;
  });

  afterEach(() => {
    global.fetch = originalFetch;
    jest.resetAllMocks();
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

  it("рендерить повідомлення про успіх при 200 OK", async () => {
    const user = userEvent.setup();
    mockFetchOnce(200);
    render(<PasswordResetRequest lang="uk" />);

    await user.type(screen.getByLabelText("Електронна пошта"), "test@example.com");
    await user.click(screen.getByRole("button", { name: "Надіслати запит" }));

    expect(
      await screen.findByText(
        "Ми надіслали інструкції з відновлення пароля на вашу електронну пошту."
      )
    ).toBeInTheDocument();
  });

  it("рендерить повідомлення про успіх при 400 (не розкриваючи існування акаунта)", async () => {
    const user = userEvent.setup();
    mockFetchOnce(400, { detail: "Bad request" });
    render(<PasswordResetRequest lang="uk" />);

    await user.type(screen.getByLabelText("Електронна пошта"), "test@example.com");
    await user.click(screen.getByRole("button", { name: "Надіслати запит" }));

    expect(
      await screen.findByText(
        "Ми надіслали інструкції з відновлення пароля на вашу електронну пошту."
      )
    ).toBeInTheDocument();
  });

  it("рендерить повідомлення про успіх при 500", async () => {
    const user = userEvent.setup();
    mockFetchOnce(500);
    render(<PasswordResetRequest lang="uk" />);

    await user.type(screen.getByLabelText("Електронна пошта"), "test@example.com");
    await user.click(screen.getByRole("button", { name: "Надіслати запит" }));

    expect(
      await screen.findByText(
        "Ми надіслали інструкції з відновлення пароля на вашу електронну пошту."
      )
    ).toBeInTheDocument();
  });

  it("рендерить повідомлення про успіх при помилці мережі (fetch reject)", async () => {
    const user = userEvent.setup();
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error("network down"));
    render(<PasswordResetRequest lang="uk" />);

    await user.type(screen.getByLabelText("Електронна пошта"), "test@example.com");
    await user.click(screen.getByRole("button", { name: "Надіслати запит" }));

    expect(
      await screen.findByText(
        "Ми надіслали інструкції з відновлення пароля на вашу електронну пошту."
      )
    ).toBeInTheDocument();
  });
});
