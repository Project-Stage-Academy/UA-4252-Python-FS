import React from 'react';
import Hero from '../components/Hero/Hero';
import StartupsGrid  from '../components/NewParticipants/StartupsGrid';
import CTASection from '../components/CTASection/CTASection';
import ForWhomGrid from '../components/ForWhomGrid/ForWhomGrid';


const Home: React.FC = () => {
  return (
    <>
      <Hero />
      <StartupsGrid />
      <CTASection />
      <ForWhomGrid />
    </>
  );
};


export default Home;
