import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import RegisterStartup from "./RegisterStartup";

jest.mock('../css/RegisterStartup.css', () => ({}));
jest.mock('../img/opentechlogo.png', () => 'opentechlogo.png');
jest.mock('../img/craftmergelogo.png', () => 'craftmergelogo.png');
jest.mock('../img/craftmergelogoblack.png', () => 'craftmergelogoblack.png');

const mockFetch = jest.fn();
global.fetch = mockFetch;

beforeEach(() => {
  mockFetch.mockClear();
  window.URL.createObjectURL = jest.fn(() => "mock-preview-url");
  window.URL.revokeObjectURL = jest.fn();
});

const fillForm = (container: HTMLElement) => {
  fireEvent.change(screen.getByPlaceholderText("Введіть назву вашої компанії"), { target: { value: "Test Company" } });
  fireEvent.change(screen.getByPlaceholderText("Введіть свою електронну пошту"), { target: { value: "test@example.com" } });
  fireEvent.change(screen.getByPlaceholderText("Введіть пароль"), { target: { value: "Password123" } });
  fireEvent.change(screen.getByPlaceholderText("Введіть пароль ще раз"), { target: { value: "Password123" } });
  fireEvent.change(screen.getByPlaceholderText("Введіть ваше прізвище"), { target: { value: "Doe" } });
  fireEvent.change(screen.getByPlaceholderText("Введіть ваше ім’я"), { target: { value: "John" } });
  const checkboxes = container.querySelectorAll('input[type="checkbox"]');
  fireEvent.click(checkboxes[0]); // Зареєстрована компанія
  fireEvent.click(checkboxes[3]); // Юридична особа
};

describe("RegisterStartup", () => {
  test("показує помилки при порожніх обов'язкових полях", async () => {
    render(<RegisterStartup />);
    fireEvent.click(screen.getAllByRole('button', { name: /Зареєструватися/i })[1]);
    expect(await screen.findByText("Не ввели назву компанії")).toBeInTheDocument();
    expect(await screen.findByText("Не ввели електронну пошту")).toBeInTheDocument();
    expect(await screen.findByText("Не ввели пароль")).toBeInTheDocument();
    expect(await screen.findByText("Не ввели ім’я")).toBeInTheDocument();
  });

  test("показує превью логотипу після вибору файлу", async () => {
    const { container } = render(<RegisterStartup />);
    const file = new File(["logo"], "logo.png", { type: "image/png" });
    const fileInput = container.querySelector('input[name="logoFile"]')!;
    fireEvent.change(fileInput, { target: { files: [file] } });
    expect(await screen.findByText("Вибрано: logo.png")).toBeInTheDocument();
    expect(screen.getByAltText("Logo preview")).toHaveAttribute("src", "mock-preview-url");
  });

  test("успішна реєстрація показує сторінку успіху", async () => {
    mockFetch.mockResolvedValueOnce({ ok: true });
    const { container } = render(<RegisterStartup />);
    fillForm(container);
    fireEvent.click(screen.getAllByRole('button', { name: /Зареєструватися/i })[1]);
    expect(await screen.findByText("Registration successful!")).toBeInTheDocument();
    expect(screen.getByText("Check your email to confirm your account.")).toBeInTheDocument();
  });

  test("помилка сервера показує повідомлення про помилку", async () => {
    mockFetch.mockResolvedValueOnce({ ok: false });
    const { container } = render(<RegisterStartup />);
    fillForm(container);
    fireEvent.click(screen.getAllByRole('button', { name: /Зареєструватися/i })[1]);
    expect(await screen.findByText("Server error. Please try again later.")).toBeInTheDocument();
  });
});
