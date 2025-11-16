import React from "react";
import "./About.scss";
import aboutImage from "../../img/about-us.jpg";

const About: React.FC = () => {
  return (
    <section className="about-wrap">
      <div className="about-container">
        <h2 className="about-title">Хто ми</h2>
        <div className="about-content">
          <div className="about-text">
            <p>
              <strong>Forum</strong> — перший форум Західної України. Наша місія — об'єднання українських виробників та стартапів і відкриття нових перспектив у виробничій галузі.
            </p>
            <p>
              <strong>Forum</strong> — це платформа для обміну досвідом, ідеями та обговорення актуальних тенденцій і передових технологій.
            </p>
            <p>
              Учасники форуму можуть ознайомитися з сучасними рішеннями виробництва крафтової продукції, підвищити впізнаваність бренду та залучити нових клієнтів. Приєднуйтесь до нашого форуму та розвивайте свій бізнес разом із нами!
            </p>
          </div>
          <div className="about-image-wrapper">
            <img src={aboutImage} alt="Форум — презентація" className="about-image" />
          </div>
        </div>
      </div>
    </section>
  );
};

export default About;
