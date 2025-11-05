import React from 'react';
import { Link } from 'react-router-dom';
import './CTASection.scss';

const CTASection: React.FC = () => {
  return (
    <div className="cta-container">
      <h2 className="cta-title">
        Майданчик для тих, хто втілює свої ідеї в життя
      </h2>
      <Link to="/register" className="cta-button">
        Долучитися
      </Link>
    </div>
  );
};

export default CTASection;
