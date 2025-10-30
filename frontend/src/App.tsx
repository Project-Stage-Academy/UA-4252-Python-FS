import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { routes } from "./routes";
import Footer from "./components/Footer/Footer";
import Header from "./components/Header/Header";
import './components/Header/Header.scss';
import "./App.css";

function App() {
  return (
    <Router>
      <div className="app-container">

        <Header />

        <div className="content">
          <Routes>
            {routes.map((r, index) => (
              <Route key={index} path={r.path} element={r.element} />
            ))}
          </Routes>
        </div>

        <Footer />
      </div>
    </Router>
  );
}

export default App;
