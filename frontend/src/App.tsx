// src/App.tsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header/Header";
import Footer from "./components/Footer/Footer";
import Home from "./pages/Home"; 
import './components/Header/Header.scss';
import "./App.css";

function App() {
  return (
    <Router>
      <div className="app-container">
        <Header />

        {/* Hero займає всю ширину і висоту */}
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>

        <Footer />
      </div>
    </Router>
  );
}

export default App;
