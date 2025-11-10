import { Suspense } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header/Header";
import Footer from "./components/Footer/Footer";
import "./components/Header/Header.scss";
import "./App.css";
import { routes } from "./routes";

function App() {
  return (
    <Router>
      <div className="app-container">
        <Header />

        <main className="content">
          <Suspense fallback={<div>Loading...</div>}>
            <Routes>
              {routes.map(r => <Route key={r.path} path={r.path} element={r.element} />)}
            </Routes>
          </Suspense>
        </main>

        <Footer />
      </div>
    </Router>
  );
}

export default App;
