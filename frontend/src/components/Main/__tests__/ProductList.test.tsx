import { render, screen, within } from "@testing-library/react";
import "@testing-library/jest-dom";
import ProductList from "../ProductList";

jest.mock("../ProductList.scss", () => ({}));

describe("ProductList", () => {
  const items = [
    {
      id: "1",
      name: "Асоціація рітейлерів України",
      image: "/src/img/Ukrainian-Retailers-Association.jpg",
      category: "Інші послуги",
      location: "Київ",
      badgeImg: "/src/img/rau.jpg",
      cta: "послуги",
    },
    {
      id: "2",
      name: "REGNO",
      image: "/src/img/wine-cheese.jpg",
      category: "Інші послуги",
      location: "Київ",
      badgeText: "REGNO",
      cta: "послуги",
    },
  ];

  it("показує заголовок пошуку та кількість", () => {
    render(<ProductList queryTitle="Сільпо" total={12} items={items} />);
    expect(screen.getByText(/результати пошуку “сільпо”/i)).toBeInTheDocument();
    expect(screen.getByText(/: 12$/)).toBeInTheDocument();
  });

  it("рендерить картки з даними", () => {
    render(<ProductList items={items} />);
    const cards = screen.getAllByRole("listitem");
    expect(cards).toHaveLength(2);

    const first = cards[0];
    expect(within(first).getByText(/асоціація рітейлерів україни/i)).toBeInTheDocument();
    expect(within(first).getByText(/інші послуги/i)).toBeInTheDocument();
    expect(within(first).getByText(/київ/i)).toBeInTheDocument();
    expect(within(first).getByRole("link", { name: /послуги/i })).toBeInTheDocument();
  });

  it("показує бейдж із текстом", () => {
    render(<ProductList items={items} />);
    expect(screen.getByText(/regno/i)).toBeInTheDocument();
  });
});
