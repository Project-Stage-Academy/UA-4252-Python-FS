import React from "react";
import "./ProductList.scss";

export type ProductCard = {
  id: string;
  name: string;
  image: string;
  location?: string;
  category?: string;
  href?: string;
  badgeText?: string;
  badgeImg?: string;
  cta?: string;
};

type Props = {
  queryTitle?: string;
  total?: number;
  items: ProductCard[];
  className?: string;
};

const ProductList: React.FC<Props> = ({ queryTitle, total, items, className }) => {
  return (
    <section className={`productlist ${className ?? ""}`.trim()}>
      {(queryTitle || typeof total === "number") && (
        <div className="productlist-header">
          {queryTitle && <h2 className="productlist-title">Результати пошуку “{queryTitle}”</h2>}
          {typeof total === "number" && <span className="productlist-count">: {total}</span>}
        </div>
      )}

      <ul className="productlist-grid" role="list">
        {items.map((it) => (
          <li key={it.id} className="product-card">
            <div className="product-card-cover">
              <img src={it.image} alt={it.name} loading="lazy" />
              {(it.badgeText || it.badgeImg) && (
                <span className="product-card-badge">
                  {it.badgeImg ? (
                    <img src={it.badgeImg} alt={it.badgeText ?? "badge"} loading="lazy" />
                  ) : (
                    it.badgeText
                  )}
                </span>
              )}
            </div>

            <div className="product-card-body">
              <div className="product-card-category">{it.category ?? "Інші послуги"}</div>
              <h3 className="product-card-title">{it.name}</h3>
              {it.location && <div className="product-card-location">{it.location}</div>}
              <a href={it.href ?? "#"} className="product-card-btn" aria-label={`Детальніше про ${it.name}`}>
                {it.cta ?? "послуги"}
              </a>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
};

export default ProductList;
