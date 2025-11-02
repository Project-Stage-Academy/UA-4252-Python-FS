import { lazy, Suspense } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header/Header";
import Footer from "./components/Footer/Footer";
import Home from "./pages/Home"; 
import './components/Header/Header.scss';
import "./App.css";

const Register = lazy(() => import("./pages/Register")); 

function App() {
  return (
    <Router>
      <div className="app-container">
        <Header />

        <Routes>
          <Route path="/" element={<Home />} />
          <Route
            path="/register"
            element={
              <Suspense fallback={null}>
                <Register />
              </Suspense>
            }
          />
        </Routes>

        <Footer />
      </div>
    </Router>
  );
}

export default App;
