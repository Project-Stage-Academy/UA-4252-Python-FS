import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import RegisterInvestor from "./RegisterInvestor";

const mockFetch = jest.fn((url, options) => {
  const body = options && typeof options === "object" ? JSON.parse((options as any).body) : {};
  if (body.email === "bob@investor.com") {
    return Promise.resolve({
      status: 400,
      json: () => Promise.resolve({ email: ["Ця електронна пошта вже зареєстрована"] }),
    });
  }
  return Promise.resolve({
    status: 201,
    json: () => Promise.resolve({ message: "success" }),
  });
});

beforeEach(() => {
  jest.clearAllMocks();
  (globalThis as any).fetch = mockFetch;
});

describe("RegisterInvestor Form", () => {
  test("показує помилки при порожніх обов'язкових полях", async () => {
    render(<RegisterInvestor />);
    fireEvent.click(screen.getByText("Зареєструватися"));

    expect(await screen.findByText("Не ввели назву компанії")).toBeInTheDocument();
    expect(await screen.findByText("Не ввели електронну пошту")).toBeInTheDocument();
    expect(await screen.findByText("Не ввели пароль")).toBeInTheDocument();
    expect(await screen.findByText("Не ввели пароль ще раз")).toBeInTheDocument();
    expect(await screen.findByText("Не ввели прізвище")).toBeInTheDocument();
    expect(await screen.findByText("Не ввели ім’я")).toBeInTheDocument();
    expect(await screen.findByText("Виберіть кого ви представляєте")).toBeInTheDocument();
    expect(await screen.findByText("Виберіть тип суб’єкта")).toBeInTheDocument();
    expect(await screen.findByText("Не ввели мінімальну інвестицію")).toBeInTheDocument();
    expect(await screen.findByText("Не ввели максимальну інвестицію")).toBeInTheDocument();
  });

  test("успішний submit показує повідомлення про підтвердження email", async () => {
    render(<RegisterInvestor />);

    fireEvent.change(screen.getByLabelText("Назва компанії"), { target: { value: "Бобер" } });
    fireEvent.change(screen.getByLabelText("Електронна пошта"), { target: { value: "alice@investor.com" } });
    fireEvent.change(screen.getByLabelText("Пароль"), { target: { value: "SecurePass123!" } });
    fireEvent.change(screen.getByLabelText("Повторіть пароль"), { target: { value: "SecurePass123!" } });
    fireEvent.change(screen.getByLabelText("Прізвище"), { target: { value: "Бобер" } });
    fireEvent.change(screen.getByLabelText("Ім’я"), { target: { value: "Боб" } });
    fireEvent.click(screen.getByLabelText("Зареєстрована компанія"));
    fireEvent.click(screen.getByLabelText("Фізична особа-підприємець"));
    fireEvent.change(screen.getByLabelText("Мінімальна інвестиція"), { target: { value: "10000" } });
    fireEvent.change(screen.getByLabelText("Максимальна інвестиція"), { target: { value: "100000" } });

    fireEvent.click(screen.getByText("Зареєструватися"));

    expect(
      await screen.findByText(/Реєстрація майже завершена/i)
    ).toBeInTheDocument();
  });

  test("показує помилку якщо email вже зареєстрований", async () => {
    render(<RegisterInvestor />);

    fireEvent.change(screen.getByLabelText("Назва компанії"), { target: { value: "Бобер" } });
    fireEvent.change(screen.getByLabelText("Електронна пошта"), { target: { value: "bob@investor.com" } });
    fireEvent.change(screen.getByLabelText("Пароль"), { target: { value: "SecurePass123!" } });
    fireEvent.change(screen.getByLabelText("Повторіть пароль"), { target: { value: "SecurePass123!" } });
    fireEvent.change(screen.getByLabelText("Прізвище"), { target: { value: "Бобер" } });
    fireEvent.change(screen.getByLabelText("Ім’я"), { target: { value: "Боб" } });
    fireEvent.click(screen.getByLabelText("Зареєстрована компанія"));
    fireEvent.click(screen.getByLabelText("Фізична особа-підприємець"));
    fireEvent.change(screen.getByLabelText("Мінімальна інвестиція"), { target: { value: "10000" } });
    fireEvent.change(screen.getByLabelText("Максимальна інвестиція"), { target: { value: "100000" } });

    fireEvent.click(screen.getByText("Зареєструватися"));

    expect(
      await screen.findByText("Ця електронна пошта вже зареєстрована")
    ).toBeInTheDocument();
  });
});
