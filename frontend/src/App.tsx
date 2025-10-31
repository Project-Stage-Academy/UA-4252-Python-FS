import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header/Header";
import Footer from "./components/Footer/Footer";
import Home from "./pages/Home"; 
import Register from "./pages/Register";
import './components/Header/Header.scss';
import "./App.css";

function App() {
  return (
    <Router>
      <div className="app-container">
        <Header />

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} /> 
        </Routes>

        <Footer />
      </div>
    </Router>
  );
}

export default App;