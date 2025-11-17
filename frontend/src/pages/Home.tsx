import React from 'react';
import Hero from '../components/Hero/Hero';
import CTASection from '../components/CTASection/CTASection';
import ForWhomGrid from '../components/ForWhomGrid/ForWhomGrid';


const Home: React.FC = () => {
  return (
    <>
      <Hero />
      <CTASection />
      <ForWhomGrid />
    </>
  );
};


export default Home;
