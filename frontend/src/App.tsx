import { lazy, Suspense } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header/Header";
import Footer from "./components/Footer/Footer";
import Home from "./pages/Home";
import PasswordResetRequest from "./pages/PasswordResetRequest";
import PasswordResetConfirm from "./pages/PasswordResetConfirm";
import "./components/Header/Header.scss";
import "./App.css";

const Register = lazy(() => import("./pages/Register"));
const WhyWorthGrid = lazy(() => import("./components/WhyWorthGrid/WhyWorthGrid"));

function App() {
  return (
    <Router>
      <div className="app-container">
        <Header />

        <main className="content">
          <Suspense fallback={null}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/register" element={<Register />} />

              <Route path="/forgot-password" element={<PasswordResetRequest />} />
              <Route path="/reset-password" element={<PasswordResetConfirm />} />

              <Route path="*" element={<div>404 Not Found</div>} />
            </Routes>

            <WhyWorthGrid />
          </Suspense>
        </main>

        <Footer />
      </div>
    </Router>
  );
}

export default App;
