import { render, screen } from "@testing-library/react";
import StartupCard from "../StartupCard";

const mockStartup = {
  id: 1,
  name: "Тестова компанія",
  category: "Інші послуги",
  shortDescription: "Короткий опис",
  location: "Україна",
  imageUrl: "/placeholder.png",
  logoUrl: "/logo-placeholder.png",
};

describe("StartupCard basic render", () => {
  test("рендерить name, category і location", () => {
    render(<StartupCard startup={mockStartup} />);
    expect(screen.getByText("Тестова компанія")).toBeInTheDocument();
    expect(screen.getByText("Інші послуги")).toBeInTheDocument();
    expect(screen.getByText("Україна")).toBeInTheDocument();
  });
});
