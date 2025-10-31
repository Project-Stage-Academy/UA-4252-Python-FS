import React from 'react';
import { useNavigate } from 'react-router-dom';
import './CTASection.scss';

const CTASection: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="cta-container">
      <h2 className="cta-title">
        Майданчик для тих, хто втілює свої ідеї в життя
      </h2>
      <button
        onClick={() => navigate('/register')}
        className="cta-button"
      >
        Долучитися
      </button>
    </div>
  );
};

export default CTASection;
