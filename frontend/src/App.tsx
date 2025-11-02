import { Suspense, lazy } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { routes } from "./routes";
import Footer from "./components/Footer/Footer";
import Header from "./components/Header/Header";

const WhyWorthGrid = lazy(() => import("./components/WhyWorthGrid/WhyWorthGrid"));

function App() {
  return (
    <Router>
      <div className="app-container">
        <Header />

        <main className="content">
          <Routes>
            {routes.map(({ path, element }) => (
              <Route key={path} path={path} element={element} />
            ))}
          </Routes>

          <Suspense fallback={null}>
            <WhyWorthGrid />
          </Suspense>
        </main>

        <Footer />
      </div>
    </Router>
  );
}

export default App;
