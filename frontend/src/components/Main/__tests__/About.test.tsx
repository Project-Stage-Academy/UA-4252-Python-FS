import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import About from "../About";

jest.mock("../About.scss", () => ({}));
jest.mock("../../img/about-us.jpg", () => "about-us.jpg");

describe("About", () => {
  it("рендерить заголовок 'Хто ми' та зображення", () => {
    render(<About />);
    expect(screen.getByRole("heading", { name: /хто ми/i })).toBeInTheDocument();

    const img = screen.getByRole("img");
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute("alt");
    expect(img.getAttribute("alt")).not.toBe("");
  });
});
