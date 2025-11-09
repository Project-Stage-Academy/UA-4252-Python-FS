import { lazy, Suspense } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header/Header";
import Footer from "./components/Footer/Footer";
import Home from "./pages/Home";
import "./components/Header/Header.scss";
import "./App.css";

// Ленивые импорты
const Register = lazy(() => import("./pages/Register"));
const PasswordResetRequest = lazy(() => import("./pages/PasswordResetRequest"));
const PasswordResetConfirm = lazy(() => import("./pages/PasswordResetConfirm"));

function App() {
  return (
    <Router>
      <div className="app-container">
        <Header />

        <main className="content">
          <Suspense fallback={<div>Loading...</div>}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/register" element={<Register />} />
              <Route path="/reset-password" element={<PasswordResetRequest />} />
              <Route path="/reset-password/confirm" element={<PasswordResetConfirm />} />
            </Routes>
          </Suspense>
        </main>

        <Footer />
      </div>
    </Router>
  );
}

export default App;
