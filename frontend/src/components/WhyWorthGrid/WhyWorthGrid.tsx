import React from "react";
import "./WhyWorthGrid.scss";

interface WhyWorthItem {
  title: string;
  description: string;
}

// TODO: replace mockData with real API data from `/api/content/landing/` 
const mockData: WhyWorthItem[] = [
  {
    title: "Прямий зв'язок з виробниками",
    description: "Знайомтеся з історією та цінностями брендів",
  },
  {
    title: "Ексклюзивні пропозиції",
    description: "Знаходьте унікальні продукти, недоступні в масовому продажі",
  },
  {
    title: "Інновації та тренди",
    description: "Будьте в курсі останніх новинок та технологій галузі",
  },
  {
    title: "Співпраця та синергія",
    description: "Об'єднуйтесь, щоб творити нове та ділитися досвідом",
  },
  {
    title: "Розвиток та масштабування",
    description: "Знаходьте нових партнерів, клієнтів та ринки збуту",
  },
  {
    title: "Підтримка та знання",
    description: "Отримуйте консультації, експертну допомогу та доступ до освітніх ресурсів",
  },
];

const WhyWorthGrid: React.FC = () => {
  return (
    <div className="why-worth-section-wrapper">
      <section className="why-worth-section">
        <h2 className="section-title">Чому варто</h2>
        <div className="grid-container">
          {mockData.map((item, i) => (
            <div
              key={i}
              className="why-worth-item"
              tabIndex={0}
              role="article"
            >
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default WhyWorthGrid;
