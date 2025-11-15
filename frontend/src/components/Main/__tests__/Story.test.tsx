import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import Story from "../Story";

jest.mock("../Story.scss", () => ({}));

describe("Story", () => {
  const sections = [
    {
      id: "about",
      heading: "Про компанію",
      html: `<p><strong>Створювати майбутнє</strong>...</p><script>evil()</script>`,
    },
    {
      id: "products",
      heading: "Інформація про товари/послуги",
      html: `<p><strong>Товари:</strong> ...</p>`,
      highlight: true,
    },
  ];

  const sidebar = [
    { label: "Повна назва", value: "Асоціація рітейлерів України" },
    { label: "ЄДРПОУ", value: "11223344" },
    { label: "Сайт", value: <a href="https://example.com">example.com</a> },
  ];

  it("рендерить секції та видаляє небезпечний HTML", () => {
    render(<Story sections={sections} sidebar={sidebar} title="Про компанію" showTOC />);
    expect(screen.getByText(/про компанію/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /інформація про товари\/послуги/i })).toBeInTheDocument();
    expect(document.querySelector("script")).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: /інформація про товари\/послуги/i })).toHaveAttribute("href", "#products");
  });

  it("додає клас is-highlight для виділеної секції", () => {
    render(<Story sections={sections} sidebar={sidebar} />);
    const highlighted = screen.getByRole("heading", { name: /інформація про товари\/послуги/i });
    expect(highlighted.closest(".story__section")).toHaveClass("is-highlight");
  });

  it("рендерить сайдбар з даними", () => {
    render(<Story sections={sections} sidebar={sidebar} />);
    expect(screen.getByText(/асоціація рітейлерів україни/i)).toBeInTheDocument();
    expect(screen.getByText("11223344")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /example\.com/i })).toHaveAttribute("href", "https://example.com");
  });
});
