import React from "react";
import "./ForWhomGrid.scss";

import craftIcon from "../../img/craft.png";
import sommelierIcon from "../../img/sommelier.png";
import hotelIcon from "../../img/hotel.png";
import retailIcon from "../../img/retail.png";
import packagingIndustryIcon from "../../img/packaging-industry.png";
import logisticsIcon from "../../img/logistics.png";
import startupIcon from "../../img/startup.png";
import othersIcon from "../../img/others.png";

interface ForWhomItem {
  title: string;
  icon: string;
}

// TODO: replace mockData with real API data from `/api/content/landing/`
const mockData: ForWhomItem[] = [
  { title: "Виробники крафтової продукції", icon: craftIcon },
  { title: "Сомельє та ресторатори", icon: sommelierIcon },
  { title: "Представники готельно-ресторанного бізнесу", icon: hotelIcon },
  { title: "Представники роздрібних та гуртових торгових мереж", icon: retailIcon },
  { title: "Представники пакувальної індустрії", icon: packagingIndustryIcon },
  { title: "Представники логістичних компаній та служб доставки", icon: logisticsIcon },
  { title: "Стартапери", icon: startupIcon },
  { title: "Інші фахівці галузі", icon: othersIcon },
];

const ForWhomGrid: React.FC = () => {
  return (
    <div className="for-whom-section-wrapper">
      <section
        className="for-whom-section"
        role="region"
        aria-labelledby="for-whom-title"
      >
        <h2 id="for-whom-title" className="section-title">
          Для кого
        </h2>
        <div className="grid-container">
          {mockData.map((item, i) => (
            <div key={i} className="for-whom-item" tabIndex={0} role="article">
              <img src={item.icon} alt="" className="item-icon" />
              <h3>{item.title}</h3>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default ForWhomGrid;
