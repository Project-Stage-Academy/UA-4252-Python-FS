import React from "react";
import type { Startup } from "./types";
import "./StartupsGrid.scss";

interface StartupCardProps {
  startup: Partial<Startup>; 
}

const StartupCard: React.FC<StartupCardProps> = ({ startup }) => {
  const name = startup.name || "Без назви";
  const shortDescription = startup.shortDescription || "";
  const category = startup.category || "";
  const location = startup.location || "Невідомо";
  const imageUrl = startup.imageUrl || "/placeholder.png";
  const logoUrl = startup.logoUrl || "/logo-placeholder.png";

  return (
    <div className="startup-card relative">
      <div className="relative">
        <img src={imageUrl} alt={name} className="card-image" />
        <img src={logoUrl} alt={`${name} logo`} className="logo" />
      </div>
      <div className="card-content">
        <p>{category}</p>
        <h3>{name}</h3>
        <p>{shortDescription}</p>
        <p className="location">{location}</p>
      </div>
    </div>
  );
};

export default StartupCard;
