import { render, screen } from "@testing-library/react";
import WhyWorthGrid from "./WhyWorthGrid";

test("renders section title", () => {
  render(<WhyWorthGrid />);
  expect(screen.getByText(/Чому варто/i)).toBeInTheDocument();
});

test("renders info blocks", async () => {
  render(<WhyWorthGrid />);
  const items = await screen.findAllByRole("article");
  expect(items.length).toBeGreaterThan(0);
});
