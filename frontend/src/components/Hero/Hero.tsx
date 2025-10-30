import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Hero.scss';
import winemaking from '../../img/winemaking.jpg';
import delivery from '../../img/delivery.jpg';
import cheese from '../../img/cheese.jpg';
import packaging from '../../img/packaging.jpg';

interface ImageItem {
  src: string;
  alt: string;
  position: string;
}

interface HeroContent {
  title: string;
  subtitle: string;
  ctaText: string;
  images: ImageItem[];
}

const mockContent: HeroContent = {
  title: 'CRAFTMERGE',
  subtitle: "Об'єднуємо крафтових виробників та інноваторів",
  ctaText: 'Детальніше про нас',
  images: [
    { src: winemaking, alt: 'ВИНОРОБСТВО', position: 'winemaking' },
    { src: delivery, alt: 'ДОСТАВКА', position: 'delivery' },
    { src: cheese, alt: 'СИРОВАРНЯ', position: 'cheese' },
    { src: packaging, alt: 'УПАКОВКА', position: 'packaging' }
  ]
};

const Hero: React.FC = () => {
  const navigate = useNavigate();
  
  // TODO: Replace mockContent with real data from API when available

  const handleCtaClick = () => {
    navigate('/register');
  };

  return (
    <section className="hero-section">
      <div className="content-container">
        <div className="text-column">
          <h1 className="title">{mockContent.title}</h1>
          <p className="subtitle">{mockContent.subtitle}</p>
          <button
            className="cta-button"
            type="button"
            onClick={handleCtaClick}
          >
            {mockContent.ctaText}
          </button>
        </div>

        <div className="image-collage">
          {mockContent.images.map((img, index) => (
            <div key={index} className={`image-wrapper ${img.position}`}>
              <img
                src={img.src}
                alt={img.alt}
                loading="lazy"
                className="collage-image"
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).src = '/assets/img-placeholder.png';
                }}
              />
              <span className="image-label">{img.alt}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Hero;
